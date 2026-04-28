# 自定义测试模板生成器

本文件用于指导如何创建自定义测试模板。

## 模板结构

一个标准的测试模板应包含以下部分：

### 1. 文件头

```python
# -*- coding: utf-8 -*-
"""
模板名称
模板描述
"""

from airtest.core.api import *
import logging
```

### 2. 配置区域

使用双花括号 `{{ variable }}` 作为变量占位符：

```python
# ============ 配置区域 ============
DEVICE_ID = "{{ device_id }}"
PACKAGE_NAME = "{{ package_name }}"
TIMEOUT = {{ timeout | default(20) }}
```

### 3. 元素定位

集中定义所有元素定位器：

```python
LOCATORS = {
    "element_name": text("显示文本"),
    "button_image": Template(r"path/to/image.png"),
    "custom_locator": (x, y)  # 坐标
}
```

### 4. 辅助函数

提供可复用的辅助方法：

```python
def wait_and_click(locator, timeout=20):
    """等待元素出现并点击"""
    wait(locator, timeout=timeout)
    touch(locator)

def safe_input(locator, text_content):
    """安全输入文本"""
    if exists(locator):
        touch(locator)
        text(text_content)
        return True
    return False
```

### 5. 测试步骤

每个测试步骤作为独立函数：

```python
def test_step_1():
    """步骤描述"""
    # 测试代码
    pass
```

### 6. 主函数

组织测试执行流程：

```python
def main():
    """执行测试"""
    try:
        # Setup
        setup()

        # 执行步骤
        test_step_1()
        test_step_2()

        # Teardown
        teardown()

        return True
    except Exception as e:
        logging.error(f"测试失败: {e}")
        snapshot(filename="error.png")
        return False
```

## 常用操作模板

### 点击操作

```python
# 文本点击
touch(text("按钮文本"))

# 图片点击
touch(Template(r"path/to/button.png"))

# 坐标点击
touch((x, y))
```

### 输入操作

```python
# 文本输入
text("输入内容")

# 先点击再输入
touch(text("输入框"))
text("内容")
```

### 等待操作

```python
# 等待元素出现
wait(text("元素"), timeout=20)

# 等待固定时间
sleep(2)
```

### 滑动操作

```python
# 方向滑动
swipe_up()
swipe_down()
swipe_left()
swipe_right()

# 自定义滑动
swipe((x1, y1), (x2, y2))
```

### 断言操作

```python
# 断言存在
assert_exists(text("元素"), "元素应该存在")

# 断言不存在
assert_not_exists(text("元素"), "元素不应该存在")

# 断言相等
assert_equal(actual, expected, "值应该相等")
```

### 截图操作

```python
# 截图
snapshot(filename="screenshot.png")

# 带描述截图
snapshot(msg="关键步骤截图")
```

## 模板变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| device_id | 设备ID | 空(自动连接) |
| package_name | 应用包名 | 空 |
| timeout | 超时时间 | 20秒 |
| username | 用户名 | - |
| password | 密码 | - |

## 最佳实践

1. **清晰的命名**: 使用描述性的函数名和变量名
2. **日志记录**: 在关键步骤添加日志
3. **错误处理**: 使用try-except捕获异常
4. **截图保存**: 在失败时保存截图
5. **参数化**: 使用模板变量实现配置化
