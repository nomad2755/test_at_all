# -*- coding: utf-8 -*-
"""
XMind 脑图生成工具包

使用方式：
    from create_xmind import create_xmind, parse_markdown, verify_xmind

    # 方式1: dict 数据
    data = {
        "root_title": "测试用例",
        "sheet_title": "功能测试",
        "branches": [
            {"title": "1. 模块A", "children": ["用例1", "用例2"]}
        ]
    }
    create_xmind(data, "output.xmind")

    # 方式2: Markdown 文本
    md = """
    # 测试用例
    ## 1. 模块A
    ### 1.1 功能描述
    - 用例1
    - 用例2
    """
    create_xmind(md, "output.xmind")

    # 方式3: JSON 字符串
    create_xmind(json_str, "output.xmind")
"""

from .create_xmind import (
    create_xmind,
    parse_markdown,
    verify_xmind,
    gen_id,
    gen_timestamp,
    validate_data
)

__all__ = [
    'create_xmind',
    'parse_markdown',
    'verify_xmind',
    'gen_id',
    'gen_timestamp',
    'validate_data'
]
