# create-xmind Skill

将 XMind 测试用例文件导入到 ZenTao 的技能。

## 功能
- 解析 XMind 文件中的测试用例
- 按优先级(P0/P1/P2)分类
- 转换为 ZenTao API 格式并提交

## 文件结构
```
create-xmind/
├── SKILL.md          # 本文件
├── scripts/
│   └── xmind_to_zentao.py  # 主脚本
└── templates/        # (可选) 模板文件
```

## 使用方法

### 命令行
```bash
python3 scripts/xmind_to_zentao.py <xmind文件> --product-id <产品ID> [--limit N] [--dry-run]
```

### 参数
- `xmind_file`: XMind 文件路径
- `--product-id`: ZenTao 产品 ID (默认 1)
- `--execution-id`: ZenTao 迭代/执行 ID (默认 24)
- `--limit`: 限制提交用例数量（用于测试）
- `--dry-run`: 仅解析不提交

## ZenTao API 关键发现 (非常重要)

### steps 字段格式 ❌→✅
ZenTao API 对 `steps` 字段有严格格式要求，错误格式会导致 UI 显示为空：

```python
# ❌ 错误格式：嵌套数组 (API 会忽略)
steps = [["打开页面", "页面显示"], ["输入验证码", "验证通过"]]

# ✅ 正确格式：对象数组
steps = [
    {"desc": "打开页面", "expect": "页面显示"},
    {"desc": "输入验证码", "expect": "验证通过"}
]
```

### Python 代码示例
```python
import json

# 构建 payload
payload = {
    "title": "测试用例标题",
    "pri": 1,  # 优先级: 1=紧急, 2=高, 3=中, 4=低
    "type": "feature",  # 类型: feature|performance|config|security|others
    "steps": [
        {"desc": "步骤1描述", "expect": "预期结果1"},
        {"desc": "步骤2描述", "expect": "预期结果2"}
    ]
}

# POST 创建
req = urllib.request.Request(
    f"{ZENTAO_URL}/products/1/testcases",
    data=json.dumps(payload).encode('utf-8'),
    headers={"Token": TOKEN, "Content-Type": "application/json"},
    method='POST'
)
```

### API 已知问题

1. **产品参数 bug**: `POST /products/{id}/testcases` 不论传什么产品ID，都会创建到产品 2
   - 解决：使用迭代端点 `POST /executions/{id}/testcases`

2. **查询返回空**: `GET /products/{id}/testcases` 返回 `total>0` 但 `cases=[]`
   - 解决：直接查询用例 `GET /testcases/{id}`

3. **软删除**: 删除用例用 `PUT /testcases/{id}` 设置 `{"deleted": "1"}`，而非 `DELETE`

### 禅道配置
- 服务器: http://192.168.0.28:9980
- API: http://192.168.0.28:9980/api.php/v1
- Token: 335bfce2adddecff7b3097534e93cf3e
- 账号: shidawei / shidawei
- 产品1(数字乡村v1.1) ID=1
- 产品2(个人数字空间) ID=2
- 迭代(邀请码专项) ID=24

## XMind 文件结构

XMind 是 ZIP 压缩包，包含以下 XML 文件：
- `content.xml` - 主题内容
- `styles.xml` - 样式
- `comments.xml` - 注释
- `meta.xml` - 元数据
- `META-INF/manifest.xml` - 清单

### 解析要点
1. 使用 `xml.etree.ElementTree` 解析 `content.xml`
2. 命名空间: `{urn:xmind:xmap:xmlns:content:2.0}`
3. 遍历 sheet → topic → children → topics 找到用例
4. 用例优先级从分类标题提取 (P0/P1/P2)
5. 步骤数据从"测试步骤"主题的子主题获取
6. **注意**: "测试步骤"主题的标题可能包含合并的步骤文本 (如 "1. xxx 2. xxx")

## 故障排除

### 步骤在 UI 显示为空
原因: `steps` 字段使用了错误的格式
解决: 确保 steps 是对象数组格式 `[{"desc": "...", "expect": "..."}]`

### 用例创建成功但查询不到
原因: API 查询 bug
解决: 直接用用例 ID 查询 `GET /testcases/{id}`

### 产品归属错误
原因: 产品参数 API bug
解决: 使用迭代端点创建用例
