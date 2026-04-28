#!/usr/bin/env python3
"""
XMind 测试用例解析器 + ZenTao 批量提交工具

功能：
1. 解析 XMind 文件，提取测试用例
2. 将用例关联到 ZenTao 产品

用法：
    python xmind_to_zentao.py <xmind文件路径> [--product-id <产品ID>] [--dry-run]
"""

import xml.etree.ElementTree as ET
import json
import sys
import argparse
import zipfile
import re
import time
import urllib.request
import urllib.error
from typing import List, Dict, Optional

# ZenTao API 配置
ZENTAO_URL = "http://192.168.0.28:9980/api.php/v1"
ZENTAO_TOKEN = "335bfce2adddecff7b3097534e93cf3e"
ZENTAO_HEADERS = {
    "Token": ZENTAO_TOKEN,
    "Content-Type": "application/json"
}

# XMind 命名空间
NS = '{urn:xmind:xmap:xmlns:content:2.0}'


def parse_xmind(xmind_path: str) -> List[Dict]:
    """解析 XMind 文件，提取测试用例"""
    test_cases = []
    
    with zipfile.ZipFile(xmind_path, 'r') as zf:
        with zf.open('content.xml') as f:
            content = f.read()
    
    root = ET.fromstring(content)
    sheet = root.find(NS + 'sheet')
    if sheet is None:
        print("❌ 未找到 sheet")
        return []
    
    root_topic = sheet.find(NS + 'topic')
    if root_topic is None:
        print("❌ 未找到根 topic")
        return []
    
    children = root_topic.find(NS + 'children')
    if children is None:
        print("❌ 未找到 children")
        return []
    
    categories_topics = children.find(NS + 'topics')
    if categories_topics is None:
        print("❌ 未找到 categories topics")
        return []
    
    categories = categories_topics.findall(NS + 'topic')
    
    for category in categories:
        category_title = category.find(NS + 'title')
        category_name = category_title.text if category_title is not None else "未分类"
        priority = extract_priority_from_category(category_name)
        
        category_children = category.find(NS + 'children')
        if category_children is None:
            continue
        category_topics = category_children.find(NS + 'topics')
        if category_topics is None:
            continue
        case_topics = category_topics.findall(NS + 'topic')
        
        for topic in case_topics:
            topic_title = topic.find(NS + 'title')
            if topic_title is None:
                continue
            title_text = topic_title.text
            
            if not title_text or any(title_text.startswith(p) for p in ['1.', '2.', '3.', '4.', '前置', '测试', '预期', '优先级']):
                continue
            
            test_case = parse_test_case(topic, title_text, priority)
            if test_case:
                test_cases.append(test_case)
    
    return test_cases


def extract_priority_from_category(category_name: str) -> str:
    if "P0" in category_name:
        return "P0"
    elif "P1" in category_name:
        return "P1"
    elif "P2" in category_name:
        return "P2"
    return "P3"


def parse_test_case(topic: ET.Element, title: str, default_pri: str) -> Optional[Dict]:
    test_case = {
        "title": title,
        "precondition": "",
        "steps": "",  # 现在存的是结构化数据
        "expected": "",
        "priority": default_pri
    }
    
    # 用于存储原始步骤和预期结果列表
    raw_steps = []
    raw_expected = []
    
    children = topic.find(NS + 'children')
    if children is not None:
        topics_container = children.find(NS + 'topics')
        if topics_container is not None:
            for child_topic in topics_container.findall(NS + 'topic'):
                child_title_elem = child_topic.find(NS + 'title')
                if child_title_elem is None:
                    continue
                child_title = child_title_elem.text
                
                if "前置条件" in child_title:
                    # 提取前置条件：去掉标题前缀
                    precond = child_title.replace('前置条件:', '').replace('前置条件', '').strip()
                    test_case["precondition"] = precond
                elif "测试步骤" in child_title:
                    raw_steps = extract_steps_with_details(child_topic)
                elif "预期结果" in child_title:
                    raw_expected = extract_expected_list(child_topic)
    
    # 合并步骤和预期结果
    test_case["steps"] = merge_steps_and_expected(raw_steps, raw_expected)
    
    return test_case


def extract_steps_with_details(topic: ET.Element) -> List[Dict]:
    """提取步骤详情（包含子步骤的 notes）"""
    steps = []
    
    # 获取主标题
    title_elem = topic.find(NS + 'title')
    if title_elem is not None and title_elem.text:
        text = title_elem.text.replace('测试步骤:', '').strip()
        if text:
            steps.append({"desc": text, "notes": ""})
    
    # 处理嵌套的子步骤
    children = topic.find(NS + 'children')
    if children is not None:
        topics_container = children.find(NS + 'topics')
        if topics_container is not None:
            for step_topic in topics_container.findall(NS + 'topic'):
                step_title = step_topic.find(NS + 'title')
                if step_title is not None and step_title.text:
                    step_text = step_title.text.strip()
                    # 提取步骤编号后的描述
                    step_match = re.match(r'^[\d一二三四五六七八九十]+[.、\s]*(.+)$', step_text)
                    if step_match:
                        step_text = step_match.group(1)
                    
                    # 检查是否有 notes (子节点内容)
                    notes = ""
                    step_children = step_topic.find(NS + 'children')
                    if step_children:
                        notes_elem = step_children.find(NS + 'notes')
                        if notes_elem is not None:
                            notes_text = ''.join(notes_elem.itertext())
                            if notes_text:
                                notes = notes_text.strip()
                    
                    steps.append({"desc": step_text, "notes": notes})
    
    return steps


def extract_expected_list(topic: ET.Element) -> List[str]:
    """提取预期结果列表"""
    expected_list = []
    
    title_elem = topic.find(NS + 'title')
    if title_elem is not None and title_elem.text:
        text = title_elem.text.replace('预期结果:', '').strip()
        if text:
            expected_list.append(text)
    
    children = topic.find(NS + 'children')
    if children is not None:
        topics_container = children.find(NS + 'topics')
        if topics_container is not None:
            for exp_topic in topics_container.findall(NS + 'topic'):
                exp_title = exp_topic.find(NS + 'title')
                if exp_title is not None and exp_title.text:
                    exp_text = exp_title.text.strip()
                    # 去掉编号
                    exp_match = re.match(r'^[\d一二三四五六七八九十]+[.、\s]*(.+)$', exp_text)
                    if exp_match:
                        exp_text = exp_match.group(1)
                    expected_list.append(exp_text)
    
    return expected_list


def merge_steps_and_expected(steps: List[Dict], expected: List[str]) -> List[Dict]:
    """将步骤和预期结果合并"""
    if not steps:
        return []
    
    # 先处理空desc：用notes填充
    for step in steps:
        if not step.get("desc") and step.get("notes"):
            step["desc"] = step["notes"]
            step["notes"] = ""
    
    result = []
    exp_idx = 0
    
    for i, step in enumerate(steps):
        step_copy = step.copy()
        
        # 跳过真正为空的步骤
        if not step_copy.get("desc"):
            continue
        
        # 分配预期结果
        if exp_idx < len(expected):
            step_copy["expect"] = expected[exp_idx]
            exp_idx += 1
        else:
            step_copy.setdefault("expect", "")
        
        result.append(step_copy)
    
    # 如果还有剩余预期结果，加到最后一个步骤
    if exp_idx < len(expected) and result:
        remaining = "\n".join(expected[exp_idx:])
        if remaining:
            result[-1]["expect"] = remaining
    
    return result


def format_steps_for_zentao(steps_data: List[Dict]) -> List[Dict]:
    """将步骤数据格式化为 ZenTao API 格式 [{desc, expect}, ...]"""
    if not steps_data:
        return []
    
    result = []
    for step in steps_data:
        desc = step.get("desc", "")
        notes = step.get("notes", "")
        expect = step.get("expect", "")
        
        # 如果 desc 为空但 notes 有内容，用 notes 作为 desc
        if not desc and notes:
            desc = notes
        elif not desc:
            continue
            
        # ZenTao 期望对象格式 {desc, expect}
        result.append({"desc": desc, "expect": expect})
    
    return result


def submit_to_zentao(test_case: Dict, product_id: int) -> Dict:
    pri_map = {"P0": 1, "P1": 2, "P2": 3, "P3": 4}
    pri = pri_map.get(test_case["priority"], 3)
    
    # 步骤数据格式化为嵌套数组格式 [[desc, expect], ...]
    steps_data = test_case.get("steps", [])
    if not isinstance(steps_data, list) or not steps_data:
        steps_formatted = []
    else:
        steps_formatted = format_steps_for_zentao(steps_data)  # 返回 list，不是 JSON 字符串
    
    payload = {
        "title": test_case["title"],
        "pri": pri,
        "type": "feature",
        "stage": "sprint",
        "steps": steps_formatted  # 直接用 list
    }
    
    if test_case.get("precondition"):
        payload["precondition"] = test_case["precondition"]
    
    url = f"{ZENTAO_URL}/products/{product_id}/testcases"
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=ZENTAO_HEADERS,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            if status == 201:
                body = resp.read().decode('utf-8')
                if body:
                    result = json.loads(body)
                    return {"success": True, "data": result}
                return {"success": True, "data": {"id": "unknown"}}
            result = json.loads(resp.read().decode('utf-8'))
            return {"success": True, "data": result}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else str(e)
        return {"success": False, "error": f"HTTP {e.code}: {error_body}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="XMind 测试用例 -> ZenTao 产品提交工具")
    parser.add_argument("xmind_file", help="XMind 文件路径")
    parser.add_argument("--product-id", "-p", type=int, default=1, help="ZenTao 产品 ID (默认: 1)")
    parser.add_argument("--dry-run", "-d", action="store_true", help="仅解析不提交")
    parser.add_argument("--limit", "-l", type=int, default=0, help="限制提交数量 (0=全部)")
    
    args = parser.parse_args()
    
    print(f"\n📖 解析 XMind 文件: {args.xmind_file}")
    test_cases = parse_xmind(args.xmind_file)
    
    if not test_cases:
        print("❌ 未找到测试用例")
        return 1
    
    print(f"✅ 共找到 {len(test_cases)} 个测试用例\n")
    
    if args.limit > 0:
        test_cases = test_cases[:args.limit]
        print(f"📋 限制提交数量: {args.limit}\n")
    
    for i, tc in enumerate(test_cases, 1):
        print(f"{i}. [{tc['priority']}] {tc['title']}")
        if tc.get('precondition'):
            print(f"   前置: {tc['precondition']}")
        if tc.get('steps'):
            steps_count = len(tc['steps'])
            first_desc = tc['steps'][0].get('desc', '') if steps_count > 0 else ''
            print(f"   步骤数: {steps_count} 首步骤: {first_desc[:30]}...")
        print()
    
    if args.dry_run:
        print("🔍 Dry-run 模式，未提交到 ZenTao")
        return 0
    
    print(f"📤 开始提交到 ZenTao 产品 ID: {args.product_id}...\n")
    
    success_count = 0
    fail_count = 0
    
    for i, tc in enumerate(test_cases, 1):
        print(f"[{i}/{len(test_cases)}] {tc['title'][:40]}...", end=" ")
        
        result = submit_to_zentao(tc, args.product_id)
        
        if result["success"]:
            print("✅")
            success_count += 1
        else:
            print(f"❌ {result['error'][:60]}")
            fail_count += 1
        
        time.sleep(0.3)
    
    print(f"\n{'='*50}")
    print(f"📊 完成: ✅ {success_count} | ❌ {fail_count}")
    print(f"{'='*50}")
    
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
