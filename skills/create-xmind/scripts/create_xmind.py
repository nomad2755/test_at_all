# -*- coding: utf-8 -*-
"""
XMind 8 脑图生成脚本

根据测试用例数据生成符合 XMind 2021 格式的 .xmind 文件。

使用方式：
    # 命令行
    python create_xmind.py -d "数据" -m "模块名" -o "输出路径"
    python create_xmind.py -f "input.json" -m "模块名"

    # 函数调用
    from create_xmind import create_xmind, md_to_xmind_data
    create_xmind(data, "output.xmind")
    create_xmind({"root_title": "测试", "branches": [...]}, "test.xmind")
"""

import zipfile
import os
import re
import uuid
import time
import argparse
import json
from typing import Union, List, Dict, Any, Optional

# ============================================================================
# 数据结构定义
# ============================================================================

def gen_id() -> str:
    """生成唯一ID"""
    return str(uuid.uuid4())

def gen_timestamp() -> int:
    """生成毫秒时间戳"""
    return int(time.time() * 1000)


# ============================================================================
# Markdown 解析
# ============================================================================

def parse_markdown(md_text: str) -> Dict[str, Any]:
    """
    解析 Markdown 格式的测试用例，转换为 XMind 数据结构

    支持的格式：
    # 根主题
    ## 1. 一级分支
    ### 1.1 二级分支
    - 子项1
    - 子项2
    ## 2. 一级分支2
    """
    lines = md_text.strip().split('\n')
    result = {
        "root_title": "",
        "sheet_title": "",
        "branches": []
    }

    current_h1 = None
    current_h2 = None
    current_h3 = None
    stack = []  # 用于追踪当前层级

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 根主题（# 标题）
        if line.startswith('# ') and not line.startswith('##'):
            result["root_title"] = line[2:].strip()
            result["sheet_title"] = result["root_title"]
            continue

        # 一级标题（## 标题）
        if line.startswith('## '):
            title = line[3:].strip()
            # 移除编号前缀（如 "1. "）
            title = re.sub(r'^\d+[\.、]\s*', '', title)

            current_h1 = {"title": title, "children": []}
            current_h2 = None
            current_h3 = None
            result["branches"].append(current_h1)
            continue

        # 二级标题（### 标题）
        if line.startswith('### '):
            title = line[4:].strip()
            title = re.sub(r'^\d+[\.、]\s*', '', title)

            if current_h1 is not None:
                current_h2 = {"title": title, "children": []}
                current_h1["children"].append(current_h2)
                current_h3 = None
            continue

        # 三级标题（#### 标题）
        if line.startswith('#### '):
            title = line[5:].strip()
            title = re.sub(r'^\d+[\.、]\s*', '', title)

            if current_h2 is not None:
                current_h3 = {"title": title, "children": []}
                current_h2["children"].append(current_h3)
            continue

        # 列表项（- 或 * 开头）
        if line.startswith('- ') or line.startswith('* '):
            item = line[2:].strip()
            if item:
                if current_h3 is not None:
                    current_h3["children"].append(item)
                elif current_h2 is not None:
                    current_h2["children"].append(item)
                elif current_h1 is not None:
                    current_h1["children"].append(item)
                else:
                    result["branches"].append(item)
            continue

        # 无序列表（带缩进的 - ）
        if re.match(r'^\s+[-*]\s+', line):
            item = re.sub(r'^\s+[-*]\s+', '', line).strip()
            if item:
                if current_h3 is not None:
                    current_h3["children"].append(item)
                elif current_h2 is not None:
                    current_h2["children"].append(item)
                elif current_h1 is not None:
                    current_h1["children"].append(item)
            continue

    return result


# ============================================================================
# 数据验证
# ============================================================================

def validate_data(data: Dict[str, Any]) -> None:
    """验证数据格式"""
    if not isinstance(data, dict):
        raise ValueError("数据必须是 dict 类型")

    if "root_title" not in data and "branches" not in data:
        # 可能是简化的数据格式，检查 branches
        if "branches" not in data:
            raise ValueError("数据必须包含 'root_title' 和 'branches' 字段")

    if "branches" in data and not isinstance(data["branches"], list):
        raise ValueError("'branches' 必须是列表")


# ============================================================================
# XMind XML 构建
# ============================================================================

def topics_to_xml(children_list: List, indent: int = 6) -> str:
    """
    将子节点列表转换为 XML 字符串

    Args:
        children_list: 子节点列表，支持字符串或字典
        indent: 缩进空格数

    Returns:
        XML 字符串
    """
    if not children_list:
        return ''

    spaces = ' ' * indent
    xml = f'{spaces}<topics type="attached">\n'

    for item in children_list:
        if isinstance(item, str):
            # 简单字符串：只包含标题
            tid = gen_id()
            ts = gen_timestamp()
            xml += f'{spaces}  <topic id="{tid}" timestamp="{ts}">\n'
            xml += f'{spaces}    <title>{escape_xml(item)}</title>\n'
            xml += f'{spaces}  </topic>\n'

        elif isinstance(item, dict):
            # 字典：包含标题和可选的子节点
            tid = gen_id()
            ts = gen_timestamp()

            # 检查是否有标记
            marker = item.get('marker', '')
            marker_attr = f' marker-id="{marker}"' if marker else ''

            xml += f'{spaces}  <topic id="{tid}" timestamp="{ts}"{marker_attr}>\n'
            xml += f'{spaces}    <title>{escape_xml(item["title"])}</title>\n'

            if 'children' in item and item['children']:
                xml += f'{spaces}    <children>\n'
                xml += topics_to_xml(item['children'], indent + 4)
                xml += f'{spaces}    </children>\n'

            xml += f'{spaces}  </topic>\n'

    xml += f'{spaces}</topics>\n'
    return xml


def escape_xml(text: str) -> str:
    """转义 XML 特殊字符"""
    if not text:
        return ''
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    return text


def build_content_xml(root_title: str, sheet_title: str, branches: List) -> str:
    """
    构建 content.xml 内容

    Args:
        root_title: 根主题标题
        sheet_title: 工作表标题
        branches: 分支列表

    Returns:
        XML 字符串
    """
    root_id = gen_id()
    root_ts = gen_timestamp()
    sheet_id = gen_id()

    children_xml = topics_to_xml(branches)

    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<xmap-content xmlns="urn:xmind:xmap:xmlns:content:2.0"
              xmlns:xhtml="http://www.w3.org/1999/xhtml"
              xmlns:fo="http://www.w3.org/1999/XSL/Format"
              xmlns:svg="http://www.w3.org/2000/svg"
              xmlns:xlink="http://www.w3.org/1999/xlink"
              version="2.0">
  <sheet id="{sheet_id}" timestamp="{root_ts}">
    <title>{escape_xml(sheet_title)}</title>
    <topic id="{root_id}" timestamp="{root_ts}">
      <title>{escape_xml(root_title)}</title>
      <children>
{children_xml}      </children>
    </topic>
  </sheet>
</xmap-content>'''

    return xml


def build_styles_xml() -> str:
    """构建 styles.xml"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<xmap-styles xmlns="urn:xmind:xmap:xmlns:style:2.0"
             xmlns:xhtml="http://www.w3.org/1999/xhtml"
             xmlns:fo="http://www.w3.org/1999/XSL/Format"
             xmlns:svg="http://www.w3.org/2000/svg"
             xmlns:xlink="http://www.w3.org/1999/xlink"
             version="2.0">
  <styles/>
</xmap-styles>'''


def build_comments_xml() -> str:
    """构建 comments.xml"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<comments xmlns="urn:xmind:xmap:xmlns:comments:2.0"
         xmlns:xhtml="http://www.w3.org/1999/xhtml"
         xmlns:fo="http://www.w3.org/1999/XSL/Format"
         xmlns:svg="http://www.w3.org/2000/svg"
         version="2.0">
</comments>'''


def build_manifest_xml() -> str:
    """构建 manifest.xml"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<manifest xmlns="urn:xmind:xmap:xmlns:envelope:2.0" version="2.0">
  <file-entry full-path="content.xml" media-type="text/xml"/>
  <file-entry full-path="styles.xml" media-type="text/xml"/>
  <file-entry full-path="comments.xml" media-type="text/xml"/>
  <file-entry full-path="META-INF/manifest.xml" media-type="text/xml"/>
  <file-entry full-path="meta.xml" media-type="text/xml"/>
  <file-entry full-path="markers/markerSheet.xml" media-type="text/xml"/>
</manifest>'''


def build_meta_xml() -> str:
    """构建 meta.xml"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<meta xmlns="urn:xmind:xmap:xmlns:meta:2.0" version="2.0">
  <Version>8</Version>
  <Build>202105270001</Build>
</meta>'''


def build_marker_sheet_xml() -> str:
    """构建 markerSheet.xml"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<marker-sheet xmlns="urn:xmind:xmap:xmlns:markers:2.0" version="2.0">
</marker-sheet>'''


# ============================================================================
# 主函数
# ============================================================================

def create_xmind(
    data: Union[Dict[str, Any], str],
    output_path: Optional[str] = None
) -> str:
    """
    创建 XMind 文件

    Args:
        data: 测试用例数据，支持：
              - dict: {"root_title": "...", "sheet_title": "...", "branches": [...]}
              - str (Markdown格式): 支持 # ## ### - 语法
              - str (JSON格式): JSON 字符串
        output_path: 输出文件路径，默认桌面

    Returns:
        生成的 XMind 文件路径

    Raises:
        ValueError: 数据格式错误
        IOError: 文件写入失败

    Example:
        >>> data = {
        ...     "root_title": "公证智能体四期测试",
        ...     "sheet_title": "测试功能点",
        ...     "branches": [
        ...         {"title": "1. 数据资产对接", "children": [
        ...             {"title": "1.1 功能描述", "children": ["对接数据资产平台"]},
        ...             {"title": "1.2 正向测试用例", "children": ["DAT-01：正常发起"]}
        ...         ]}
        ...     ]
        ... }
        >>> path = create_xmind(data, "测试用例.xmind")
        >>> print(f"已生成: {path}")
    """
    # 数据解析
    if isinstance(data, str):
        # 尝试 JSON 解析
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            # 不是 JSON，尝试 Markdown 解析
            data = parse_markdown(data)

    # 验证数据
    validate_data(data)

    # 设置默认值
    root_title = data.get("root_title", "测试用例")
    sheet_title = data.get("sheet_title", root_title)
    branches = data.get("branches", [])

    # 生成输出路径
    if output_path is None:
        import tempfile
        output_path = os.path.join(tempfile.gettempdir(), 'output.xmind')

    # 确保扩展名正确
    if not output_path.endswith('.xmind'):
        output_path += '.xmind'

    # 构建 XML 内容
    content_xml = build_content_xml(root_title, sheet_title, branches)

    # 创建 ZIP 文件
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('content.xml', content_xml.encode('utf-8'))
        z.writestr('META-INF/manifest.xml', build_manifest_xml().encode('utf-8'))
        z.writestr('styles.xml', build_styles_xml().encode('utf-8'))
        z.writestr('comments.xml', build_comments_xml().encode('utf-8'))
        z.writestr('meta.xml', build_meta_xml().encode('utf-8'))
        z.writestr('markers/markerSheet.xml', build_marker_sheet_xml().encode('utf-8'))

    print(f'XMind 文件已生成: {output_path}')
    print(f'文件大小: {os.path.getsize(output_path):,} 字节')

    return output_path


def verify_xmind(path: str) -> bool:
    """
    验证 XMind 文件是否有效

    Args:
        path: XMind 文件路径

    Returns:
        True 表示有效，False 表示无效
    """
    try:
        with zipfile.ZipFile(path, 'r') as z:
            # 检查必需文件
            required_files = [
                'content.xml',
                'styles.xml',
                'comments.xml',
                'meta.xml',
                'META-INF/manifest.xml'
            ]

            namelist = z.namelist()
            for f in required_files:
                if f not in namelist:
                    print(f'缺少必需文件: {f}')
                    return False

            # 检查 content.xml 格式
            content = z.read('content.xml').decode('utf-8')
            if '<?xml' not in content:
                print('content.xml 格式错误')
                return False

            # 检查根主题
            if '<topic' not in content:
                print('未找到根主题')
                return False

        print(f'[OK] File verified: {path}')
        return True

    except Exception as e:
        print(f'验证失败: {e}')
        return False


# ============================================================================
# 命令行接口
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='生成 XMind 脑图文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 从 Markdown 文本生成
  python create_xmind.py -d "# 测试\\n## 1. 模块\\n- 用例1\\n- 用例2"

  # 从文件读取
  python create_xmind.py -f "测试用例.md"

  # 指定输出路径
  python create_xmind.py -d "..." -m "我的测试" -o "C:/Users/Desktop/"

  # 验证已生成的 XMind 文件
  python create_xmind.py --verify "C:/Users/Desktop/测试.xmind"
'''
    )

    parser.add_argument(
        '-d', '--data',
        help='测试用例数据（Markdown 或 JSON 格式）'
    )

    parser.add_argument(
        '-f', '--file',
        help='从文件读取测试用例数据'
    )

    parser.add_argument(
        '-m', '--module',
        help='模块名称（用于输出文件名）'
    )

    parser.add_argument(
        '-o', '--output',
        help='输出目录或完整路径'
    )

    parser.add_argument(
        '--verify',
        help='验证已生成的 XMind 文件'
    )

    args = parser.parse_args()

    # 验证模式
    if args.verify:
        verify_xmind(args.verify)
        return

    # 获取数据
    data = None

    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            data = f.read()
    elif args.data:
        data = args.data
    else:
        parser.print_help()
        return

    # 确定输出路径
    output_path = None

    if args.output:
        if os.path.isdir(args.output):
            # 是目录，生成文件名
            module_name = args.module or '测试用例'
            # 清理文件名
            module_name = re.sub(r'[<>:"/\\|?*]', '_', module_name)
            output_path = os.path.join(args.output, f'{module_name}.xmind')
        else:
            # 是文件路径
            output_path = args.output

    # 生成 XMind
    create_xmind(data, output_path)

    # 验证
    if output_path:
        verify_xmind(output_path)


if __name__ == '__main__':
    main()
