#!/usr/bin/env python3
"""
auto_module_lookup.py - 从测试计划排期表自动匹配模块信息
用法:
    python3 scripts/auto_module_lookup.py <关键词>    # 搜索匹配模块
    python3 scripts/auto_module_lookup.py --all       # 列出所有模块
    python3 scripts/auto_module_lookup.py --all-json   # JSON格式输出所有模块
"""

import pandas as pd
import sys
import os
import json

EXCEL_PATH = "/root/.openclaw/browser/openclaw/user-data/测试计划排期表.xlsx"

def load_sheets():
    """加载所有sheet，使用pandas跳过有问题的sheet"""
    sheets = {}
    xl = pd.ExcelFile(EXCEL_PATH)
    for name in xl.sheet_names:
        try:
            # 有问题的sheet用openpyxl直接跳过，只用pandas读取能读的
            if "(2)" in name or "备份" in name:
                continue
            df = pd.read_excel(xl, sheet_name=name, header=None)
            sheets[name] = df
        except Exception as e:
            print(f"⚠️ 跳过Sheet '{name}': {e}", file=sys.stderr)
    return sheets

def parse_accounts_sheet(df):
    """解析账号信息 sheet (主表)"""
    modules = []
    
    # 找到表头行
    header_row = None
    for i, row in df.iterrows():
        row_vals = [str(v).strip() if pd.notna(v) else "" for v in row]
        if "项目" in row_vals[0] and "环境" in row_vals[1]:
            header_row = i
            break
    
    if header_row is None:
        header_row = 0
    
    # 解析数据行
    for i in range(header_row + 1, len(df)):
        row = df.iloc[i]
        vals = [str(v).strip() if pd.notna(v) else "" for v in row]
        
        project = vals[0]  # 项目
        env = vals[1]      # 环境
        platform = vals[2] # 平台
        module_name = vals[3] # 业务版块
        url = vals[4]      # URL
        accounts = vals[5] # 账号/密码/角色
        db_info = vals[6]  # 数据库
        owner = vals[7]    # 负责人
        remark = vals[8]   # 备注
        
        if module_name and module_name not in ["业务版块", "URL", "账号/密码", "角色", "负责人", "项目", "环境", "平台", "None", ""]:
            modules.append({
                "name": module_name,
                "project": project,
                "env": env,
                "platform": platform,
                "url": url,
                "accounts": accounts,
                "owner": owner,
                "remark": remark
            })
    
    return modules

def parse_accounts2_sheet(df):
    """解析账号信息(2) sheet (项目跟踪表)"""
    projects = []
    
    # 找表头
    header_row = None
    for i, row in df.iterrows():
        row_vals = [str(v).strip() if pd.notna(v) else "" for v in row]
        if "项目" in row_vals[0] and "环境" in row_vals[1]:
            header_row = i
            break
    
    if header_row is None:
        header_row = 0
    
    for i in range(header_row + 1, len(df)):
        row = df.iloc[i]
        vals = [str(v).strip() if pd.notna(v) else "" for v in row]
        
        project = vals[0]
        env = vals[1]
        role = vals[2]
        url = vals[3]
        accounts = vals[4]
        db_info = vals[5]
        remark = vals[6]
        owner = vals[7]
        
        if project and project not in ["项目", "None", ""]:
            projects.append({
                "name": project,
                "env": env,
                "role": role,
                "url": url,
                "accounts": accounts,
                "owner": owner,
                "remark": remark
            })
    
    return projects

def build_keyword_index(modules, projects):
    """建立关键词索引，方便快速查找"""
    index = {}
    
    all_items = []
    for m in modules:
        all_items.append(("module", m))
    for p in projects:
        all_items.append(("project", p))
    
    # 关键词同义词映射
    synonyms = {
        "个人app": ["个人app", "个人APP", "app", "APP", "移动端", "手机端", "天优app", "天优APP"],
        "数字家园": ["数字家园", "我的数字家园", "个人数字空间", "数字空间", "数字档案", "个人空间"],
        "电商": ["短视频电商", "数字商城", "电商", "商城"],
        "版权": ["数字版权", "版权", "版权管理"],
        "碳汇": ["碳汇", "碳足迹", "碳汇服务"],
        "知识库": ["知识库"],
        "后台": ["后台", "管理平台", "大后台", "后台管理", "管控平台"],
        "pad": ["pad", "PAD", "安卓"],
        "pc": ["pc端", "pc", "PC", "电脑端", "红色pc", "红色PC"],
        "ai小优": ["ai小优", "AI小优", "小优", "ai小优新版", "新版ai"],
        "物理资产": ["物理资产", "资产"],
        "生态价值": ["生态价值", "生态价值资产"],
        "活立木": ["活立木", "活立"],
        "文化资产": ["文化资产", "文化"],
        "生态农场": ["生态农场", "农场"],
        "数字资产运营": ["数字资产运营", "运营服务平台", "运营平台"],
        "法律智能体": ["法律智能体", "法律"],
        "公证智能体": ["公证智能体", "公证"],
        "价值评估": ["价值评估", "评估智能体"],
        "东方数碳": ["东方数碳", "数碳"],
        "智能客服": ["智能客服", "客服"],
        "专利": ["专利", "专利管理"],
        "黄陂人民医院": ["黄陂人民医院", "人民医院", "医院"],
        "短视频": ["短视频", "视频电商"],
    }
    
    for item_type, item in all_items:
        name = item["name"].lower()
        
        # 直接用名字建索引
        for kw in name.replace(" ", "").split("/"):
            if len(kw) >= 2:
                if kw not in index:
                    index[kw] = []
                index[kw].append((item_type, item))
        
        # 用同义词建索引
        for std_kw, variants in synonyms.items():
            if any(v.lower() in name for v in variants):
                if std_kw not in index:
                    index[std_kw] = []
                index[std_kw].append((item_type, item))
    
    return index, synonyms

def search(keyword, index, synonyms):
    """搜索匹配模块"""
    keyword = keyword.lower().strip()
    results_list = []
    results_keys = set()
    
    for kw in keyword.replace(" ", "").split("/"):
        if kw in index:
            for r in index[kw]:
                key = (r[0], r[1]['name'])
                if key not in results_keys:
                    results_keys.add(key)
                    results_list.append(r)
    
    # 2. 同义词扩展搜索
    for std_kw, variants in synonyms.items():
        if keyword in std_kw or std_kw in keyword:
            if std_kw in index:
                for r in index[std_kw]:
                    key = (r[0], r[1]['name'])
                    if key not in results_keys:
                        results_keys.add(key)
                        results_list.append(r)
    
    # 3. 关键词任意字匹配
    for kw in keyword:
        if len(kw) >= 2:
            for idx_kw, idx_items in index.items():
                if kw in idx_kw:
                    for r in idx_items:
                        key = (r[0], r[1]['name'])
                        if key not in results_keys:
                            results_keys.add(key)
                            results_list.append(r)
    
    return results_list

def format_result(item_type, item, verbose=False):
    """格式化单个结果"""
    if item_type == "module":
        lines = [f"📦 【{item['name']}】"]
        if item.get("project") and item["project"] not in ["", "None"]:
            lines.append(f"   🏷️ 项目: {item['project']}")
        if item.get("env") and item["env"] not in ["", "None"]:
            lines.append(f"   🌍 环境: {item['env']}")
        if item.get("platform") and item["platform"] not in ["", "None"]:
            lines.append(f"   🖥️ 平台: {item['platform']}")
        if item.get("url") and item["url"] not in ["", "None"]:
            lines.append(f"   🔗 URL: {item['url']}")
        if item.get("accounts") and item["accounts"] not in ["", "None"]:
            # 截取前100字符
            acc = item["accounts"][:100]
            if len(item["accounts"]) > 100:
                acc += "..."
            lines.append(f"   👤 账号: {acc}")
        if item.get("owner") and item["owner"] not in ["", "None"]:
            lines.append(f"   👥 负责人: {item['owner']}")
    else:
        lines = [f"📋 【{item['name']}】"]
        if item.get("env") and item["env"] not in ["", "None"]:
            lines.append(f"   🌍 环境: {item['env']}")
        if item.get("role") and item["role"] not in ["", "None"]:
            lines.append(f"   🎭 角色: {item['role']}")
        if item.get("url") and item["url"] not in ["", "None"]:
            lines.append(f"   🔗 URL: {item['url']}")
        if item.get("accounts") and item["accounts"] not in ["", "None"]:
            acc = item["accounts"][:100]
            if len(item["accounts"]) > 100:
                acc += "..."
            lines.append(f"   👤 账号: {acc}")
        if item.get("owner") and item["owner"] not in ["", "None"]:
            lines.append(f"   👥 负责人: {item['owner']}")
    
    return "\n".join(lines)

def get_assignee(module_name, index):
    """根据模块名获取指派人"""
    results = search(module_name, index, {})
    for item_type, item in results:
        owner = item.get("owner", "")
        if owner and owner not in ["", "None"]:
            # 映射到 ZenTao 账号
            owner_map = {
                "石大卫": "shidawei",
                "张文骏": "zhangwenjun",
                "刘偲": "liusi",
                "张海棠": "HTang",
            }
            return owner_map.get(owner, owner), item.get("name", "")
    return None, None

if __name__ == "__main__":
    print("📊 正在加载测试计划排期表...", file=sys.stderr)
    sheets = load_sheets()
    
    modules = []
    projects = []
    
    for name, df in sheets.items():
        if "账号信息" == name or name.startswith("账号信息 ") and "(2)" not in name:
            modules = parse_accounts_sheet(df)
        elif "账号信息" in name and "(2)" in name:
            projects = parse_accounts2_sheet(df)
    
    index, synonyms = build_keyword_index(modules, projects)
    
    if len(sys.argv) < 2:
        print(f"""
🔍 模块自动识别工具

用法:
  python3 scripts/auto_module_lookup.py <关键词>   # 搜索模块
  python3 scripts/auto_module_lookup.py --all       # 列出所有模块
  python3 scripts/auto_module_lookup.py --json      # JSON格式输出

已加载: {len(modules)} 个业务版块, {len(projects)} 个测试项目
示例关键词: 个人app/pc/后台/版权/碳汇/知识库/电商/ai小优/数字家园/物理资产
        """)
        sys.exit(0)
    
    arg = sys.argv[1]
    
    if arg == "--all":
        print(f"\n📋 全部业务版块 ({len(modules)} 个):")
        print("-" * 60)
        for m in modules:
            print(f"\n【{m['name']}】")
            if m.get("env"): print(f"   🌍 {m['env']}")
            if m.get("owner"): print(f"   👥 {m['owner']}")
        
        print(f"\n\n📋 全部测试项目 ({len(projects)} 个):")
        print("-" * 60)
        for p in projects:
            print(f"\n【{p['name']}】")
            if p.get("env"): print(f"   🌍 {p['env']}")
            if p.get("role"): print(f"   🎭 {p['role']}")
            if p.get("owner"): print(f"   👥 {p['owner']}")
    
    elif arg == "--json":
        print(json.dumps({
            "modules": modules,
            "projects": projects
        }, ensure_ascii=False, indent=2))
    
    else:
        results = search(arg, index, synonyms)
        
        if results:
            print(f"\n🔍 「{arg}」匹配到 {len(results)} 个结果:\n")
            seen = set()
            for item_type, item in results:
                key = (item_type, item["name"])
                if key in seen:
                    continue
                seen.add(key)
                print(format_result(item_type, item))
                print()
            
            # 给出指派建议
            assignee, matched_name = get_assignee(arg, index)
            if assignee:
                print(f"💡 指派建议: {assignee} (负责「{matched_name}」)")
        else:
            print(f"❌ 没有找到匹配「{arg}」的模块")
            print(f"\n💡 尝试的关键词: {', '.join(synonyms.keys())}")