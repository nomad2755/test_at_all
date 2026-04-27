# ZenTao Integration Skill

ZenTao 禅道集成技能 - 用于管理需求、测试用例、Bug等。

## 功能

- ✅ 创建需求文档（Story）及子需求
- ✅ 创建测试用例并关联到需求
- ✅ 批量导入测试用例
- ✅ 创建测试用例模块
- ✅ 查询和验证数据

## 重要发现（经验总结）

### 1. 测试用例关联需求

**关键发现**: 使用 `parent` 字段关联测试用例到需求，而不是 `story` 字段！

```python
# ❌ 错误方式 - story字段不生效
data = {"title": "用例标题", "story": 需求ID}

# ✅ 正确方式 - 使用parent字段
data = {"title": "用例标题", "parent": 需求ID}
```

### 2. Steps 字段格式

**关键发现**: `steps` 必须传 JSON 数组，不能是字符串！

```python
# ❌ 错误方式 - 字符串格式
data = {"steps": "[{\"desc\":\"步骤\",\"expect\":\"预期\"}]"}

# ✅ 正确方式 - 数组格式
data = {"steps": [{"desc": "步骤", "expect": "预期"}]}
```

### 3. 创建时的产品ID问题

- 产品1创建的需求/测试用例可能在UI上显示不正常
- 建议使用产品2创建测试用例
- 创建后验证 `product` 字段

### 4. HTTP 502 处理

批量导入时偶发502错误，需要重试机制。

## API 端点

### 基础配置
- **Base URL**: `http://192.168.0.28:9980/api.php/v1`
- **Token**: `335bfce2adddecff7b3097534e93cf3e`（可能过期，需重新认证）
- **认证方式**: `POST /tokens` with `{"account":"shidawei","password":"shidawei"}`

### 需求(Stories)
```
GET    /products/{productID}/stories          # 获取需求列表
POST   /products/{productID}/stories           # 创建需求
PUT    /stories/{storyID}                     # 更新需求
```

### 测试用例
```
GET    /products/{productID}/testcases        # 获取测试用例（可能有分页问题）
POST   /products/{productID}/testcases         # 创建测试用例
GET    /testcases/{id}                         # 获取单个测试用例
PUT    /testcases/{id}                         # 更新测试用例
```

### 测试用例模块
```
GET    /products/{productID}/testcase-modules  # 获取模块列表
POST   /products/{productID}/testcase-modules  # 创建模块
```

### 迭代/执行
```
GET    /projects/{projectID}/executions        # 获取迭代列表
POST   /projects/{projectID}/executions        # 创建迭代
```

## 使用示例

### 1. 创建需求

```python
# 创建主需求
data = {
    "title": "【内测邀请码管理系统】用户端邀请码申请与管理功能",
    "type": "story",
    "pri": 1,
    "product": 1,
    "status": "draft"
}
story = api_post("products/1/stories", data)
# 返回: {"id": 4, ...}

# 创建子需求
data = {
    "title": "【邀请码登录】邀请码登录功能",
    "type": "story",
    "parent": 4,  # 关联主需求
    "product": 1
}
sub_story = api_post("products/1/stories", data)
# 返回: {"id": 5, ...}
```

### 2. 创建测试用例（关联需求）

```python
data = {
    "title": "【TC-LOGIN-001】正常邀请码登录流程",
    "pri": 1,
    "type": "feature",
    "parent": 5,  # ✅ 关联到需求ID 5
    "steps": [
        {"desc": "用户打开登录页面", "expect": "显示登录表单"},
        {"desc": "输入有效的邀请码", "expect": "邀请码被接受"},
        {"desc": "点击登录按钮", "expect": "登录成功"}
    ]
}
tc = api_post("products/2/testcases", data)
```

### 3. 批量导入测试用例

```bash
python3 scripts/batch_import_cases.py
```

## 已知问题

1. **测试用例 steps 字段 bug**: 通过某些endpoint创建的用例，steps可能为空
2. **产品ID混淆**: API有时会将用例创建到错误的产品
3. **HTTP 502**: 批量操作时偶发，需要重试

## 文件结构

```
zentao-integration/
├── SKILL.md                      # 本文件
├── scripts/
│   ├── create_stories.py         # 创建需求脚本
│   ├── create_testcases.py      # 创建测试用例脚本
│   ├── batch_import_cases.py    # 批量导入测试用例
│   └── zentao_api.py            # API基础类
└── README.md
```

## 安全注意

- Token 包含敏感信息，不要在日志中输出完整Token
- 定期检查Token是否过期
