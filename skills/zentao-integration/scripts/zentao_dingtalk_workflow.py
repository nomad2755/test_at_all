#!/usr/bin/env python3
"""
禅道测试工作流 + 钉钉通知
功能：创建测试用例 → 导入禅道 → 发送钉钉通知
"""

import json
import requests
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional

# ============ 配置 ============
ZENTAO_BASE = "http://192.168.0.28:9980/api.php/v1"
ZENTAO_TOKEN = "cf2da27b8b734b419352d844bc451a14"
ZENTAO_HEADERS = {
    "Token": ZENTAO_TOKEN,
    "Content-Type": "application/json"
}

# 钉钉 Webhook（可通过环境变量覆盖）
DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN"
DINGTALK_SECRET = ""  # 如果安全设置是加签模式，填入 secret


class DingTalkNotifier:
    """钉钉通知器"""
    
    def __init__(self, webhook_url: str = None, secret: str = None):
        self.webhook_url = webhook_url or DINGTALK_WEBHOOK
        self.secret = secret or DINGTALK_SECRET
    
    def send_markdown(self, title: str, text: str) -> bool:
        """
        发送 Markdown 格式消息到钉钉群
        
        Args:
            title: 消息标题
            text: Markdown 格式内容
            
        Returns:
            bool: 发送是否成功
        """
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": text
            }
        }
        
        # 安全设置：关键词模式
        # 在 text 中包含"测试报告"关键词
        
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            result = response.json()
            
            if result.get("errcode") == 0:
                print(f"✅ 钉钉通知发送成功")
                return True
            else:
                print(f"❌ 钉钉通知失败: {result.get('errmsg')}")
                return False
        except Exception as e:
            print(f"❌ 钉钉通知异常: {e}")
            return False
    
    def send_test_report(self, task_title: str, task_id: str, 
                        total_cases: int, created_cases: int,
                        report_summary: str = "") -> bool:
        """
        发送测试报告到钉钉群
        
        Args:
            task_title: 禅道任务标题
            task_id: 任务 ID
            total_cases: 用例总数
            created_cases: 已创建用例数
            report_summary: AI 生成的报告摘要
        """
        zentao_url = f"http://192.168.0.28:9980"
        
        markdown_content = f"""# 测试报告 📋

## 任务信息
- **任务标题**: {task_title}
- **禅道任务**: [ID: {task_id}]({zentao_url}/task-view-{task_id}.html)
- **执行时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 测试用例统计
| 类型 | 数量 |
|------|------|
| 用例总数 | {total_cases} |
| 已创建 | {created_cases} |

## 报告摘要
{report_summary or '测试用例已成功创建并导入禅道。'}

---
🤖 由测试助手自动生成
"""
        
        return self.send_markdown("测试报告", markdown_content)
    
    def send_bug_report(self, bug_id: int, title: str, 
                       severity: str, steps: str) -> bool:
        """
        发送 Bug 报告到钉钉群
        """
        zentao_url = f"http://192.168.0.28:9980"
        
        severity_emoji = {
            "1": "🔴",
            "2": "🟠", 
            "3": "🟡",
            "4": "🔵"
        }.get(str(severity), "⚪")
        
        markdown_content = f"""# 🐛 新建 Bug

## Bug 信息
- **Bug ID**: [{bug_id}]({zentao_url}/bug-view-{bug_id}.html)
- **标题**: {title}
- **严重程度**: {severity_emoji} {'致命' if severity == '1' else '严重' if severity == '2' else '一般' if severity == '3' else '优化'}

## 复现步骤
{steps}

---
🤖 由测试助手自动创建
"""
        
        return self.send_markdown(f"🐛 新建 Bug: {title[:30]}...", markdown_content)


class ZenTaoDingTalkWorkflow:
    """
    禅道 + 钉钉 工作流
    整合测试用例创建和钉钉通知
    """
    
    def __init__(self, zentao_token: str = None, dingtalk_webhook: str = None):
        self.zentao_token = zentao_token or ZENTAO_TOKEN
        self.zentao_base = ZENTAO_BASE
        self.headers = {
            "Token": self.zentao_token,
            "Content-Type": "application/json"
        }
        self.dingtalk = DingTalkNotifier(webhook_url=dingtalk_webhook)
    
    def create_test_case(self, title: str, pri: int = 3, 
                        steps: List[Dict[str, str]] = None,
                        type_: str = "feature",
                        product_id: int = 2) -> Optional[int]:
        """
        创建测试用例
        
        Args:
            title: 用例标题
            pri: 优先级 (1-4)
            steps: 步骤列表 [{"desc": "步骤", "expect": "预期"}]
            type_: 用例类型 (feature/performance/config/security/others)
            product_id: 产品 ID (2=个人数字空间)
            
        Returns:
            int: 创建的用例 ID，失败返回 None
        """
        url = f"{self.zentao_base}/products/{product_id}/testcases"
        
        data = {
            "title": title,
            "pri": pri,
            "type": type_,
            "steps": steps or [{"desc": "待补充", "expect": "待补充"}]
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            
            if response.status_code == 201:
                result = response.json()
                case_id = result.get("id") or result.get("data", {}).get("id")
                print(f"✅ 测试用例创建成功: {title} (ID: {case_id})")
                return case_id
            else:
                print(f"❌ 测试用例创建失败: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ 测试用例创建异常: {e}")
            return None
    
    def batch_create_cases(self, cases: List[Dict[str, Any]], 
                          product_id: int = 2) -> Dict[str, int]:
        """
        批量创建测试用例
        
        Args:
            cases: 用例列表
            [
                {
                    "title": "用例标题",
                    "pri": 1,
                    "steps": [{"desc": "步骤", "expect": "预期"}],
                    "type": "feature"
                }
            ]
            product_id: 产品 ID
            
        Returns:
            {"total": 10, "success": 8, "failed": 2}
        """
        results = {"total": len(cases), "success": 0, "failed": 0}
        
        for case in cases:
            case_id = self.create_test_case(
                title=case.get("title"),
                pri=case.get("pri", 3),
                steps=case.get("steps"),
                type_=case.get("type", "feature"),
                product_id=product_id
            )
            
            if case_id:
                results["success"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    def run(self, task_title: str, task_id: str,
            cases: List[Dict[str, Any]] = None,
            report_summary: str = "",
            product_id: int = 2) -> Dict[str, Any]:
        """
        运行完整工作流：创建用例 → 钉钉通知
        
        Args:
            task_title: 禅道任务标题
            task_id: 禅道任务 ID
            cases: 测试用例列表
            report_summary: 报告摘要
            product_id: 产品 ID
            
        Returns:
            工作流执行结果
        """
        print(f"\n{'='*50}")
        print(f"🚀 禅道测试工作流启动")
        print(f"{'='*50}")
        print(f"任务: {task_title} (ID: {task_id})")
        print(f"产品ID: {product_id}")
        print(f"用例数量: {len(cases) if cases else 0}")
        print()
        
        # 1. 创建测试用例
        if cases:
            print("📝 正在创建测试用例...")
            create_result = self.batch_create_cases(cases, product_id)
            print(f"   创建结果: 成功 {create_result['success']}, 失败 {create_result['failed']}")
        else:
            create_result = {"total": 0, "success": 0, "failed": 0}
        
        # 2. 发送钉钉通知
        print("\n📤 正在发送钉钉通知...")
        notify_result = self.dingtalk.send_test_report(
            task_title=task_title,
            task_id=task_id,
            total_cases=create_result["total"],
            created_cases=create_result["success"],
            report_summary=report_summary
        )
        
        print(f"\n{'='*50}")
        print(f"✅ 工作流执行完成")
        print(f"{'='*50}")
        
        return {
            "success": create_result["success"] > 0 and notify_result,
            "cases_created": create_result["success"],
            "cases_failed": create_result["failed"],
            "dingtalk_notified": notify_result
        }


def main():
    parser = argparse.ArgumentParser(description="禅道测试工作流 + 钉钉通知")
    parser.add_argument("--task-id", type=str, required=True, help="禅道任务 ID")
    parser.add_argument("--task-title", type=str, required=True, help="任务标题")
    parser.add_argument("--case-count", type=int, default=5, help="生成用例数量")
    parser.add_argument("--product-id", type=int, default=2, help="产品 ID")
    parser.add_argument("--webhook", type=str, help="钉钉 Webhook URL")
    
    args = parser.parse_args()
    
    # 示例：用 LLM 生成测试用例（或从文件读取）
    sample_cases = [
        {
            "title": f"测试用例-{i}",
            "pri": 3,
            "steps": [{"desc": f"步骤{i}.1", "expect": f"预期{i}.1"}],
            "type": "feature"
        }
        for i in range(1, args.case_count + 1)
    ]
    
    workflow = ZenTaoDingTalkWorkflow(dingtalk_webhook=args.webhook)
    result = workflow.run(
        task_title=args.task_title,
        task_id=args.task_id,
        cases=sample_cases
    )
    
    print(f"\n执行结果: {json.dumps(result, ensure_ascii=False, indent=2)}")


if __name__ == "__main__":
    main()
