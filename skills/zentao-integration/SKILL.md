---
name: zentao-integration
description: ZenTao bug tracking API integration. Query, create and update bugs, get statistics.
license: MIT
---

# ZenTao Bug 跟踪集成

## 概述

通过 API 与禅道 (ZenTao) 系统集成，实现 Bug 的查询、创建、更新和统计分析。

## 服务器信息

| 项目 | 值 |
|------|-----|
| 服务器 | http://192.168.0.28:9980 |
| 产品 | 数字乡村 v1.1 (ID: 1) |
| 迭代 | 邀请码专项 (ID: 24) |

## 认证

```python
import requests

base_url = "http://192.168.0.28:9980"
api_url = f"{base_url}/api.php/v1"

# 登录获取 token
def login(account, password):
    response = requests.post(f"{api_url}/tokens", json={
        "account": account,
        "password": password
    })
    return response.json()["token"]

token = login("shidawei", "shidawei")
```

## API 操作

### 1. 查询 Bug 列表

```bash
# 产品所有 Bug
curl "http://192.168.0.28:9980/api.php/v1/products/1/bugs" \
  -H "Token: 335bfce2adddecff7b3097534e93cf3e"

# 带分页
curl "http://192.168.0.28:9980/api.php/v1/products/1/bugs?limit=20&page=1" \
  -H "Token: xxx"
```

```python
def get_product_bugs(product_id=1, limit=20, page=1):
    url = f"{api_url}/products/{product_id}/bugs"
    params = {"limit": limit, "page": page}
    headers = {"Token": token}
    response = requests.get(url, headers=headers, params=params)
    return response.json()
```

### 2. 查询指定 Bug

```bash
curl "http://192.168.0.28:9980/api.php/v1/bugs/9727" \
  -H "Token: xxx"
```

```python
def get_bug(bug_id):
    url = f"{api_url}/bugs/{bug_id}"
    headers = {"Token": token}
    response = requests.get(url, headers=headers)
    return response.json()
```

### 3. 创建 Bug

```bash
curl -X POST "http://192.168.0.28:9980/api.php/v1/products/1/bugs" \
  -H "Content-Type: application/json" \
  -H "Token: xxx" \
  -d '{
    "title": "Bug 标题",
    "severity": 3,
    "pri": 2,
    "type": "codeerror",
    "steps": "<p>重现步骤</p>",
    "openedBuild": ["trunk"]
  }'
```

```python
def create_bug(product_id, bug_data):
    url = f"{api_url}/products/{product_id}/bugs"
    headers = {
        "Token": token,
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=bug_data)
    return response.json()
```

### 4. 更新 Bug

```python
def update_bug(bug_id, update_data):
    url = f"{api_url}/bugs/{bug_id}"
    headers = {
        "Token": token,
        "Content-Type": "application/json"
    }
    response = requests.put(url, headers=headers, json=update_data)
    return response.json()

# 添加分析内容
update_bug(9727, {
    "steps": "<p>【问题描述】</p><p>xxx</p><p>【可能原因】</p><p>1. xxx</p>"
})
```

### 5. 查询迭代 Bug

```bash
curl "http://192.168.0.28:9980/api.php/v1/executions/24/bugs" \
  -H "Token: xxx"
```

### 6. 获取产品/执行列表

```bash
# 产品列表
curl "http://192.168.0.28:9980/api.php/v1/products" -H "Token: xxx"

# 迭代列表
curl "http://192.168.0.28:9980/api.php/v1/executions" -H "Token: xxx"
```

## 字段说明

### Bug 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| title | string | Bug 标题 (必填) |
| severity | int | 严重程度 1-4 (P0-P3) |
| pri | int | 优先级 1-4 |
| type | string | Bug 类型: codeerror, config, install... |
| steps | string | 重现步骤 (HTML 格式) |
| openedBuild | array | 版本 Build |
| assignedTo | string | 指派人 |
| module | int | 模块 ID |

### Severity 严重程度

| 值 | 级别 | 说明 |
|----|------|------|
| 1 | P0 | 阻断 - 功能完全不可用 |
| 2 | P1 | 严重 - 核心功能异常 |
| 3 | P2 | 一般 - 非核心功能问题 |
| 4 | P3 | 轻微 - 不影响使用 |

### Bug 状态

| 状态 | 说明 |
|------|------|
| active | 激活 |
| resolved | 已解决 |
| closed | 已关闭 |

## 使用示例

### 示例 1: 创建 Bug

```python
bug_data = {
    "title": "【邀请码】页面无法正常打开",
    "severity": 3,
    "pri": 2,
    "type": "codeerror",
    "steps": "<p>【步骤】</p><p>1. 打开链接</p><p>【结果】页面空白</p>",
    "openedBuild": ["trunk"]
}
result = create_bug(1, bug_data)
print(f"Bug ID: {result['id']}")
```

### 示例 2: 添加分析到已有 Bug

```python
analysis = """
<p>【问题描述】</p>
<p>申请的界面可以使用登录的短信验证码</p>
<p>【可能原因】</p>
<p>1. 验证逻辑混用</p>
<p>2. 权限打通</p>
<p>【建议检查点】</p>
<p>1. 检查后端逻辑</p>
"""

update_bug(9727, {"steps": analysis})
```

### 示例 3: 统计 Bug 状态

```python
def get_bug_stats(product_id=1):
    bugs = get_product_bugs(product_id, limit=100)["bugs"]
    stats = {"active": 0, "resolved": 0, "closed": 0}
    for b in bugs:
        stats[b["status"]] = stats.get(b["status"], 0) + 1
    return stats
```

## 触发关键词

- "禅道"
- "ZenTao"
- "查询 Bug"
- "创建 Bug"
- "更新 Bug"
- "Bug 统计"
- "添加分析"