#!/usr/bin/env python3
"""
auto_bug_creator.py - 智能 Bug 创建工具
自动根据 Bug 描述从测试计划排期表匹配模块、环境、账号、指派人

用法:
    python3 scripts/auto_bug_creator.py <Bug描述> [严重程度1-5] [优先级1-4] [--screenshot]
    python3 scripts/auto_bug_creator.py --test   # 测试模式（不实际提交）
    python3 scripts/auto_bug_creator.py --screenshot   # 自动上传最新截图并添加到 Bug

示例:
    python3 scripts/auto_bug_creator.py "我的数字家园里面的照片按钮点击没有反应"
    python3 scripts/auto_bug_creator.py "电商模块无法下单" 3 2
    python3 scripts/auto_bug_creator.py "登录失败" --screenshot
"""


import pandas as pd
import sys
import os
import json
import re
import urllib.request
import urllib.parse
import uuid

EXCEL_PATH = "/root/.openclaw/browser/openclaw/user-data/测试计划排期表.xlsx"
ZENDAO_URL = "http://192.168.0.28:9980/api.php/v1"
ZENDAO_TOKEN = "edfa8ff0c698a2286131b4f60ffa8811"  # 2026-05-12 更新

# 数字资产管理平台配置（截图上传）
WHHNHY_URL = "https://www.whhnhy.com:8966"
UPLOAD_API = f"{WHHNHY_URL}/admin-api/infra/file/upload"
LOGIN_API = f"{WHHNHY_URL}/admin/login"
UPLOAD_ACCOUNT = "admin"
UPLOAD_PASSWORD = "Szxc@2024"

# 全局缓存
_modules_cache = None
_projects_cache = None
_index_cache = None
_synonyms_cache = None

# 指派人映射（姓名 → ZenTao 账号）
ASSIGNEE_MAP = {
    "石大卫": "shidawei",
    "张文骏": "zhangwenjun",
    "刘偲": "liusi",
    "张海棠": "HTang",
}

# 通用测试账号（无明确模块归属时使用）
DEFAULT_ACCOUNT = "18671450802"
DEFAULT_PASSWORD = "a123456"
DEFAULT_URL = "https://whhnhy.com:38868"


def load_data():
    """加载并缓存测试计划排期表数据"""
    global _modules_cache, _projects_cache, _index_cache, _synonyms_cache
    
    if _modules_cache is not None:
        return _modules_cache, _projects_cache, _index_cache, _synonyms_cache
    
    sheets = {}
    xl = pd.ExcelFile(EXCEL_PATH)
    for name in xl.sheet_names:
        try:
            if "(2)" in name or "备份" in name:
                continue
            df = pd.read_excel(xl, sheet_name=name, header=None)
            sheets[name] = df
        except Exception as e:
            print(f"⚠️ 跳过Sheet '{name}': {e}", file=sys.stderr)
    
    modules = []
    projects = []
    
    for name, df in sheets.items():
        if name == "账号信息":
            modules = parse_accounts_sheet(df)
        elif "账号信息" in name and "(2)" not in name:
            pass
    
    # 也从账号信息(2)获取项目信息
    try:
        df2 = pd.read_excel(xl, sheet_name="账号信息 (2)", header=None)
        projects = parse_accounts2_sheet(df2)
    except:
        pass
    
    index, synonyms = build_keyword_index(modules, projects)
    
    _modules_cache = modules
    _projects_cache = projects
    _index_cache = index
    _synonyms_cache = synonyms
    
    return modules, projects, index, synonyms


def parse_accounts_sheet(df):
    """解析账号信息 sheet"""
    modules = []
    header_row = 0
    for i, row in df.iterrows():
        row_vals = [str(v).strip() if pd.notna(v) else "" for v in row]
        if "项目" in row_vals[0] and "环境" in row_vals[1]:
            header_row = i
            break
    
    for i in range(header_row + 1, len(df)):
        row = df.iloc[i]
        vals = [str(v).strip() if pd.notna(v) else "" for v in row]
        
        project = vals[0]
        env = vals[1]
        platform = vals[2]
        module_name = vals[3]
        url = vals[4]
        accounts = vals[5]
        owner = vals[7]
        
        if module_name and module_name not in ["业务版块", "URL", "账号/密码", "角色", "负责人", "项目", "环境", "平台", "None", ""]:
            modules.append({
                "name": module_name,
                "project": project,
                "env": env,
                "platform": platform,
                "url": url,
                "accounts": accounts,
                "owner": owner,
            })
    
    return modules


def parse_accounts2_sheet(df):
    """解析账号信息(2) sheet"""
    projects = []
    header_row = 0
    for i, row in df.iterrows():
        row_vals = [str(v).strip() if pd.notna(v) else "" for v in row]
        if "项目" in row_vals[0] and "环境" in row_vals[1]:
            header_row = i
            break
    
    for i in range(header_row + 1, len(df)):
        row = df.iloc[i]
        vals = [str(v).strip() if pd.notna(v) else "" for v in row]
        
        project = vals[0]
        env = vals[1]
        role = vals[2]
        url = vals[3]
        accounts = vals[4]
        owner = vals[7]
        
        if project and project not in ["项目", "None", ""]:
            projects.append({
                "name": project,
                "env": env,
                "role": role,
                "url": url,
                "accounts": accounts,
                "owner": owner,
            })
    
    return projects


def build_keyword_index(modules, projects):
    """建立关键词索引"""
    index = {}
    
    synonyms = {
        "个人app": ["个人app", "个人APP", "app", "APP", "移动端", "手机端", "天优app", "天优APP"],
        "数字家园": ["数字家园", "我的数字家园", "个人数字空间", "数字空间", "数字档案", "个人空间"],
        "电商": ["短视频电商", "数字商城", "电商", "商城"],
        "版权": ["数字版权", "版权", "版权管理"],
        "碳汇": ["碳汇", "碳足迹", "碳汇服务"],
        "知识库": ["知识库"],
        "后台": ["后台", "管理平台", "大后台", "后台管理", "管控平台", "管控"],
        "pad": ["pad", "PAD", "安卓"],
        "pc": ["pc端", "pc", "PC", "电脑端", "红色pc", "红色PC"],
        "ai小优": ["ai小优", "AI小优", "小优", "ai小优新版", "新版ai", "AI小优新版"],
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
        "登录": ["登录", "登入", "login"],
        "拍照": ["拍照", "照片", "相机", "相册", "camera", "photo"],
    }
    
    all_items = []
    for m in modules:
        all_items.append(("module", m))
    for p in projects:
        all_items.append(("project", p))
    
    for item_type, item in all_items:
        name = item["name"].lower()
        for kw in name.replace(" ", "").split("/"):
            if len(kw) >= 2:
                if kw not in index:
                    index[kw] = []
                index[kw].append((item_type, item))
        
        for std_kw, variants in synonyms.items():
            if any(v.lower() in name for v in variants):
                if std_kw not in index:
                    index[std_kw] = []
                index[std_kw].append((item_type, item))
    
    return index, synonyms


def search(keyword, index, synonyms):
    """搜索匹配"""
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
    
    for std_kw, variants in synonyms.items():
        if keyword in std_kw or std_kw in keyword:
            if std_kw in index:
                for r in index[std_kw]:
                    key = (r[0], r[1]['name'])
                    if key not in results_keys:
                        results_keys.add(key)
                        results_list.append(r)
    
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


def extract_keywords_from_desc(desc):
    """从 Bug 描述中提取关键词"""
    # 先尝试完整匹配
    modules, _, index, synonyms = load_data()
    
    # 按优先级尝试匹配
    priority_keywords = [
        "个人app", "个人APP", "个人数字空间", "数字家园",
        "电商", "版权", "碳汇", "知识库", "后台", "pad",
        "pc", "ai小优", "物理资产", "活立木", "文化资产",
        "法律智能体", "公证智能体", "价值评估", "智能客服",
        "登录", "拍照", "照片"
    ]
    
    found = []
    for kw in priority_keywords:
        if kw.lower() in desc.lower():
            found.append(kw)
    
    return found


def identify_module(bug_desc):
    """根据 Bug 描述自动识别模块"""
    modules, projects, index, synonyms = load_data()
    
    # 个人APP/数字空间 硬编码映射（表格中这些行数据不完整，缺少URL和负责人）
    # key 名称必须与 extract_keywords_from_desc 的 priority_keywords 一致
    personal_app_map = {
        "数字家园": {
            "module": "个人数字空间",
            "module_id": 295,
            "url": "https://whhnhy.com:38868",
            "account": "18671450802",
            "password": "a123456",
            "assignee": "shidawei",
            "owner": "石大卫",
        },
        "个人数字空间": {
            "module": "个人数字空间",
            "module_id": 295,
            "url": "https://whhnhy.com:38868",
            "account": "18671450802",
            "password": "a123456",
            "assignee": "shidawei",
            "owner": "石大卫",
        },
        "个人app": {
            "module": "个人APP",
            "module_id": 156,
            "url": "https://whhnhy.com:38868",
            "account": "18671450802",
            "password": "a123456",
            "assignee": "shidawei",
            "owner": "石大卫",
        },
    }
    
    keywords = extract_keywords_from_desc(bug_desc)
    
    # 1. 先检查个人APP硬编码映射表
    for kw in keywords:
        if kw in personal_app_map:
            info = personal_app_map[kw].copy()
            info["matched_keyword"] = kw
            info["source"] = "personal_app_map"
            return info
    
    # 2. 从关键词索引中搜索
    for kw in keywords:
        results = search(kw, index, synonyms)
        if results:
            item_type, item = results[0]
            owner = item.get("owner", "")
            assignee = ASSIGNEE_MAP.get(owner, owner) if owner else "shidawei"
            
            # 获取测试账号
            accounts = item.get("accounts", "")
            account = DEFAULT_ACCOUNT
            password = DEFAULT_PASSWORD
            if accounts and accounts not in ["", "None"]:
                # 尝试从 accounts 字符串中提取第一个账号
                match = re.search(r'(\d{11,})/([^\n：:]+)', accounts)
                if match:
                    account = match.group(1)
                    password = match.group(2).strip()
            
            return {
                "module": item["name"],
                "module_id": item.get("module_id", 0),
                "url": item.get("url", DEFAULT_URL) or DEFAULT_URL,
                "account": account,
                "password": password,
                "assignee": assignee,
                "owner": owner,
                "matched_keyword": kw,
                "source": "module" if item_type == "module" else "project"
            }
    
    # 默认返回通用信息
    return {
        "module": "通用",
        "module_id": 0,
        "url": DEFAULT_URL,
        "account": DEFAULT_ACCOUNT,
        "password": DEFAULT_PASSWORD,
        "assignee": "shidawei",
        "owner": "石大卫",
        "matched_keyword": None,
        "source": "default"
    }


def get_zentao_token():
    """获取或刷新 ZenTao Token"""
    import json
    
    # 先尝试现有 token
    req = urllib.request.Request(
        f"{ZENDAO_URL}/bugs?product=1&page=1&limit=1",
        headers={"Token": ZENDAO_TOKEN}
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                return ZENDAO_TOKEN
    except:
        pass
    
    # token 无效，重新获取
    data = json.dumps({"account": "shidawei", "password": "shidawei"}).encode()
    req = urllib.request.Request(
        f"{ZENDAO_URL}/tokens",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read())
        return result.get("token", ZENDAO_TOKEN)




def get_upload_token_and_cookies():
    """
    使用 Playwright 登录数字资产管理平台，获取 token 和 cookies
    返回: (access_token, cookie_str)
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ 需要安装 playwright: pip install playwright && playwright install chromium")
        return None, None

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        try:
            page.goto(LOGIN_API, timeout=20000, wait_until='domcontentloaded')
            page.wait_for_timeout(1000)

            page.fill('input[placeholder="请输入用户名"]', UPLOAD_ACCOUNT)
            page.fill('input[placeholder="请输入密码"]', UPLOAD_PASSWORD)
            page.click('button')
            page.wait_for_url('**/admin/**', timeout=10000)
            page.wait_for_timeout(2000)

            page.goto(f"{WHHNHY_URL}/admin/infra/file/file", timeout=20000, wait_until='domcontentloaded')
            page.wait_for_timeout(2000)

            access_token_json = page.evaluate('localStorage.getItem("ACCESS_TOKEN")')
            access_token_data = json.loads(access_token_json)
            access_token = json.loads(access_token_data['v'])
            cookies = page.context.cookies()
            cookie_str = '; '.join([f"{c['name']}={c['value']}" for c in cookies])

            return access_token, cookie_str

        except Exception as e:
            print(f"❌ 登录数字资产管理平台失败: {e}")
            return None, None
        finally:
            browser.close()


def upload_screenshot(image_path, access_token=None, cookie_str=None):
    """
    上传图片到数字资产管理平台，返回永久 URL
    image_path: 图片本地路径
    返回: 永久 URL 或 None
    """
    if not os.path.exists(image_path):
        print(f"❌ 文件不存在: {image_path}")
        return None

    if not access_token or not cookie_str:
        print("🔐 正在获取登录态...")
        access_token, cookie_str = get_upload_token_and_cookies()
        if not access_token or not cookie_str:
            return None

    with open(image_path, 'rb') as f:
        image_data = f.read()
    filename = os.path.basename(image_path)
    boundary = '----WebKitFormBoundary' + str(uuid.uuid4().int)[:16]

    header = ('--' + boundary + '\r\n'
               'Content-Disposition: form-data; name="file"; filename="' + filename + '"\r\n'
               'Content-Type: image/png\r\n'
               '\r\n').encode()
    footer = ('\r\n--' + boundary + '--\r\n').encode()
    body = header + image_data + footer

    req = urllib.request.Request(UPLOAD_API, data=body, method='POST')
    req.add_header('Cookie', cookie_str)
    req.add_header('Content-Type', 'multipart/form-data; boundary=' + boundary)
    req.add_header('Authorization', 'Bearer ' + access_token)
    req.add_header('User-Agent', 'Mozilla/5.0')

    try:
        response = urllib.request.urlopen(req, timeout=30)
        result = response.read().decode()
        resp_data = json.loads(result)
        if resp_data.get('code') == 200:
            permanent_url = resp_data.get('data')
            return permanent_url
        else:
            print(f"❌ 上传失败: {result}")
            return None

    except urllib.error.HTTPError as e:
        print(f"❌ HTTP错误 {e.code}: {e.read().decode()[:200]}")
        return None
    except Exception as e:
        print(f"❌ 上传异常: {e}")
        return None


def get_latest_screenshot():
    """获取最新的截图文件"""
    inbound_dir = '/root/.openclaw/media/inbound'

    if not os.path.exists(inbound_dir):
        return None

    import glob
    files = glob.glob(os.path.join(inbound_dir, '*.png')) + \
            glob.glob(os.path.join(inbound_dir, '*.jpg')) + \
            glob.glob(os.path.join(inbound_dir, '*.jpeg'))

    if not files:
        return None

    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]


def create_bug(title, steps, severity=3, pri=3, assignee="shidawei", module_id=0, test_mode=False):
    """创建 Bug"""
    token = get_zentao_token()
    
    bug_data = {
        "product": 1,
        "title": title,
        "severity": severity,
        "pri": pri,
        "type": "function",
        "steps": steps,
        "openedBuild": "trunk",
        "assignedTo": assignee,
    }
    
    if module_id:
        bug_data["module"] = module_id
    
    data = json.dumps(bug_data).encode()
    req = urllib.request.Request(
        f"{ZENDAO_URL}/bugs",
        data=data,
        headers={
            "Token": token,
            "Content-Type": "application/json"
        }
    )
    
    if test_mode:
        print("🧪 测试模式 - 不实际提交 Bug")
        print(f"   标题: {title}")
        print(f"   模块ID: {module_id}")
        print(f"   严重程度: {severity}")
        print(f"   优先级: {pri}")
        print(f"   指派给: {assignee}")
        print(f"   步骤长度: {len(steps)} 字符")
        return {"id": "TEST", "title": title, "test_mode": True}
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        return {"error": str(e), "body": error_body}


def build_steps(module_info, bug_desc, steps_text, screenshot_url=None):
    """构建 Bug steps HTML"""
    url = module_info["url"]
    account = module_info["account"]
    password = module_info["password"]
    
    # 根据模块判断设备和环境
    if "app" in module_info["module"].lower() or "个人" in module_info["module"]:
        device_hint = "iOS模拟器 / Android测试机"
    elif "pad" in module_info["module"].lower():
        device_hint = "Android PAD设备"
    else:
        device_hint = "Chrome浏览器 / Edge浏览器"
    
    # 截图 URL
    screenshot_display = screenshot_url if screenshot_url else "暂无"
    
    steps = f"""<p>【环境】</p><p>- 测试地址：{url}</p><p>- 模块：{module_info['module']}</p><p>- 设备：{device_hint}</p><p>【账号密码】</p><p>- 用户名：{account}</p><p>- 密码：{password}</p><p>【前置条件】</p><p>1. </p><p>【操作步骤】</p><p>{steps_text}</p><p>【期望结果】</p><p>1. </p><p>【实际结果】</p><p>1. {bug_desc}</p><p>【附截图】</p><p>{screenshot_display}</p>"""
    
    return steps


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    
    if sys.argv[1] == "--test":
        print("🧪 测试模式演示")
        print("-" * 60)
        test_cases = [
            "我的数字家园里面的照片按钮点击没有反应",
            "电商模块无法下单",
            "后台管理登录失败",
            "PC端版权页面无法上传文件",
        ]
        for desc in test_cases:
            info = identify_module(desc)
            print(f"\n📝 Bug描述: {desc}")
            print(f"   → 识别模块: {info['module']} (来源: {info['source']}, 关键词: {info['matched_keyword']})")
            print(f"   → URL: {info['url']}")
            print(f"   → 账号: {info['account']} / {info['password']}")
            print(f"   → 指派给: {info['assignee']} ({info['owner']})")
        sys.exit(0)
    
    # 解析参数
    severity = 3
    pri = 3
    test_mode = False
    auto_screenshot = False
    screenshot_url = None  # 截图永久 URL
    
    args = sys.argv[1:]
    if "--dry-run" in args or "-n" in args:
        test_mode = True
        args = [a for a in args if a not in ["--dry-run", "-n"]]
    if "--screenshot" in args:
        auto_screenshot = True
        args = [a for a in args if a != "--screenshot"]
    
    if len(args) >= 2:
        try:
            severity = int(args[-2])
            pri = int(args[-1])
            bug_desc = " ".join(args[:-2])
        except ValueError:
            bug_desc = " ".join(args)
    else:
        bug_desc = args[0]
    
    # 自动上传截图
    if auto_screenshot:
        print("📤 正在自动上传最新截图...")
        latest_img = get_latest_screenshot()
        if latest_img:
            print(f"   截图文件: {latest_img}")
            screenshot_url = upload_screenshot(latest_img)
            if screenshot_url:
                print(f"   永久 URL: {screenshot_url}")
            else:
                print("   ⚠️ 截图上传失败，将不添加截图")
        else:
            print("   ⚠️ 未找到截图文件")
    
    # 自动识别模块
    print("🔍 正在分析 Bug 描述...")
    module_info = identify_module(bug_desc)
    
    print(f"""
📋 Bug 信息确认
{'='*60}
  Bug 描述: {bug_desc}
  识别模块: {module_info['module']} (模块ID: {module_info.get('module_id', 0)}, 匹配关键词: {module_info['matched_keyword']})
  测试地址: {module_info['url']}
  测试账号: {module_info['account']} / {module_info['password']}
  指派给:   {module_info['assignee']} ({module_info['owner']})
  严重程度: {severity} (1=致命, 3=一般)
  优先级:   {pri} (1=紧急, 3=中)
{'='*60}
""")
    
    # 确认提交
    if not test_mode:
        confirm = input("是否提交 Bug? (y/n): ").strip().lower()
        if confirm not in ["y", "yes", "是"]:
            print("❌ 已取消")
            sys.exit(0)
    
    # 构建标题和 steps
    # 智能生成模块前缀
    title_prefix = module_info['module']
    if title_prefix == "通用":
        # 尝试从描述推断
        for kw in ["登录", "登入"] if any(kw in bug_desc for kw in ["登录", "登入"]) else []:
            title_prefix = kw
        if title_prefix == "通用":
            title_prefix = "通用"
    
    title = f"【{title_prefix}】{bug_desc}"
    steps = build_steps(module_info, bug_desc, "<p>1. </p>", screenshot_url)
    
    # 如果有截图，更新 steps 中的"暂无"
    if screenshot_url:
        steps = steps.replace("<p>暂无</p>", f"<p>{screenshot_url}</p>")
    
    print("\n🚀 正在提交 Bug...")
    result = create_bug(title, steps, severity, pri, module_info["assignee"], module_info.get("module_id", 0), test_mode=test_mode)
    
    if "error" in result:
        print(f"❌ 提交失败: {result['error']}")
        print(f"   详情: {result.get('body', '')}")
        sys.exit(1)
    elif result.get("test_mode"):
        print(f"\n✅ 测试模式完成（未实际提交）")
    else:
        bug_id = result.get("id", "未知")
        print(f"""
✅ Bug 创建成功！
   Bug ID: #{bug_id}
   标题: {title}
   指派给: {module_info['assignee']}
""")
    
    return result


if __name__ == "__main__":
    main()