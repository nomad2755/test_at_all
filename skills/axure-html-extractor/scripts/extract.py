#!/usr/bin/env python3
"""
Axure HTML 原型需求提取工具（curl 法）

用法:
    python3 scripts/extract.py <BASE_URL> <PAGE_ID> <PAGE_NAME> [OUTPUT_DIR]

示例:
    python3 scripts/extract.py \
        "https://www.whhnhy.com:37777/axure/digital-asset/sjzcyyfwpt12" \
        "wu2oxn" \
        "数据登记列表（四期）" \
        "/root/.openclaw/workspace/test-team/docs"
"""
import re
import sys
import os
import subprocess

def fetch(url, timeout="10 30"):
    """用 curl 下载 URL 内容"""
    result = subprocess.run(
        ['curl', '-s', '--connect-timeout', timeout.split()[0], '-m', timeout.split()[1], url],
        capture_output=True, text=True
    )
    return result.stdout

def find_page_file(doc_js, page_id):
    """从 document.js 中找到页面对应的 HTML 文件名"""
    # 格式: "wu2oxn",bq="数据登记列表（四期）",br="数据登记列表（四期）.html"
    patterns = [
        rf'"{page_id}"[^,]*bq="([^"]+)"[^,]*br="([^"]+\.html)"',
        rf'"{page_id}"[^"]*"([^"]+\.html)"',
    ]
    for pattern in patterns:
        match = re.search(pattern, doc_js)
        if match:
            if len(match.groups()) == 2:
                return match.group(2), match.group(1)
            else:
                return match.group(1), None
    return None, None

def extract_text(html):
    """从 HTML 提取纯文本"""
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_fields(text):
    """解析字段列表"""
    fields = []
    # 匹配 * 字段名：
    pattern = r'\* ([^：\n]+)：?\s*'
    for m in re.finditer(pattern, text):
        field_name = m.group(1).strip()
        if field_name and len(field_name) > 1 and len(field_name) < 30:
            fields.append(field_name)
    return fields

def parse_rules(text):
    """解析业务规则"""
    rules = {}
    
    # 字段规则
    field_rules = re.search(r'字段规则\s*([\s\S]+?)(?=交互规则|页面交互|$)', text)
    if field_rules:
        rules['field'] = field_rules.group(1).strip()
    
    # 交互规则
    interaction = re.search(r'交互规则\s*([\s\S]+?)(?=取消|提交|存草稿|$)', text)
    if interaction:
        rules['interaction'] = interaction.group(1).strip()
    
    return rules

def parse_buttons(text):
    """解析按钮"""
    buttons = re.findall(r'(取消|提交|存草稿|重置|删除|编辑|查看|上一步|下一步|确认)[^取消提交存草稿]*', text)
    return list(set(buttons))

def generate_doc(page_name, page_id, text, fields, rules, buttons, output_path):
    """生成需求文档"""
    import datetime
    
    doc = f"""# {page_name} - 需求文档

> **来源：** Axure 原型页面
> **页面 ID：** {page_id}
> **生成时间：** {datetime.datetime.now().strftime('%Y-%m-%d')}

---

## 一、页面概述

- **页面名称：** {page_name}
- **页面 ID：** {page_id}

---

## 二、表单字段

"""
    if fields:
        doc += "| 字段名 | 说明 |\n|--------|------|\n"
        for f in fields:
            doc += f"| {f} |  |\n"
    else:
        doc += "*（未识别到明确字段，可能是列表页面）*\n"

    doc += "\n## 三、业务规则\n\n"
    if 'field' in rules:
        doc += f"### 字段规则\n\n{rules['field']}\n\n"
    else:
        doc += "*（未找到明确的字段规则段落）*\n"

    doc += "\n## 四、交互规则\n\n"
    if 'interaction' in rules:
        doc += f"{rules['interaction']}\n"
    else:
        doc += "*（未找到明确的交互规则段落）*\n"

    doc += "\n## 五、页面操作\n\n"
    if buttons:
        doc += "按钮：" + "、".join(buttons) + "\n"
    else:
        doc += "*（未识别到按钮）*\n"

    doc += f"""
---

## 六、完整文本内容（供参考）

```
{text[:10000]}
```

*（内容已截断，仅展示前 10000 字符）*
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(doc)
    
    return output_path

def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    page_id = sys.argv[2]
    page_name = sys.argv[3]
    output_dir = sys.argv[4] if len(sys.argv) > 4 else '/tmp'
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"正在提取: {page_name} ({page_id})")
    
    # 1. 获取 document.js
    print("  [1/5] 获取页面索引 document.js...")
    doc_js = fetch(f"{base_url}/data/document.js")
    if not doc_js or len(doc_js) < 100:
        print("  ⚠️ document.js 获取失败，尝试备选路径...")
        doc_js = fetch(f"{base_url}/resources/scripts/axure/doc.js")
    
    # 2. 查找页面文件
    print("  [2/5] 查找页面对应文件...")
    page_file, found_name = find_page_file(doc_js, page_id)
    if not page_file:
        # 尝试用页面名搜索
        search = re.search(rf'"([^"]+\.html)".*?{re.escape(page_name)}', doc_js)
        if search:
            page_file = search.group(1)
            print(f"  ⚠️ 用页面名搜索到: {page_file}")
        else:
            # 直接用页面名作为文件名
            page_file = f"{page_name}.html"
            print(f"  ⚠️ 未找到，使用默认文件名: {page_file}")
    
    print(f"  ✅ 找到文件: {page_file}")
    
    # 3. 下载页面 HTML
    print("  [3/5] 下载页面 HTML...")
    html = fetch(f"{base_url}/{page_file}?id={page_id}")
    if len(html) < 1000:
        print(f"  ❌ 页面内容过小 ({len(html)} 字节)，尝试直接用页面名访问...")
        html = fetch(f"{base_url}/{page_name}.html?id={page_id}")
    
    if len(html) < 1000:
        print(f"  ❌ 页面内容过小 ({len(html)} 字节)，下载可能失败")
        sys.exit(1)
    print(f"  ✅ 下载成功: {len(html)} 字节")
    
    # 4. 提取内容
    print("  [4/5] 提取并解析内容...")
    text = extract_text(html)
    fields = parse_fields(text)
    rules = parse_rules(text)
    buttons = parse_buttons(text)
    print(f"  ✅ 提取到 {len(fields)} 个字段")
    
    # 5. 生成文档
    print("  [5/5] 生成需求文档...")
    output_file = os.path.join(output_dir, f"requirements_{page_id}.md")
    generate_doc(page_name, page_id, text, fields, rules, buttons, output_file)
    
    print(f"\n✅ 完成！需求文档已保存到:\n  {output_file}")
    print(f"   字段: {len(fields)} 个")
    print(f"   文本长度: {len(text)} 字符")

if __name__ == "__main__":
    main()
