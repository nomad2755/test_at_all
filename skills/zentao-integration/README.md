# ZenTao Integration

ZenTao 禅道 API 集成技能。

## 快速开始

### 1. 安装依赖
```bash
pip install requests
```

### 2. 配置
编辑脚本中的配置：
- `BASE_URL`: ZenTao 服务器地址
- `TOKEN`: 认证 Token
- `PRODUCT_ID`: 产品 ID

### 3. 创建需求
```bash
python3 scripts/create_stories.py
```

### 4. 批量导入测试用例
```bash
python3 scripts/batch_import_cases.py
```

## 重要说明

### 测试用例关联需求
使用 `parent` 字段关联测试用例到需求：
```python
data = {
    "title": "【TC-XXX】用例标题",
    "parent": 需求ID,  # 不是 story 字段！
    "steps": [{"desc": "步骤", "expect": "预期"}]
}
```

### Steps 格式
steps 必须是 JSON 数组：
```python
"steps": [{"desc": "步骤1", "expect": "预期1"}, {"desc": "步骤2", "expect": "预期2"}]
```

## 禅道服务器

- 地址: http://192.168.0.28:9980
- 账号: shidawei
- 产品ID: 1 (数字乡村), 2 (个人数字空间)
