---
name: airtest-automation
description: |
  这是一个全面的Airtest自动化测试技能，支持移动端和Windows应用的UI自动化测试。
  当用户需要执行以下操作时触发：
  1. 执行Airtest自动化测试（如点击、滑动、图像识别）
  2. 通过ADB控制Android设备（安装/卸载应用、启动/停止应用）
  3. 根据自然语言描述生成自动化测试脚本
  4. 管理、执行和查看历史测试脚本
  触发关键词包括："Airtest测试"、"ADB控制"、"生成测试脚本"、"执行测试用例"、"自动化测试"
---

# Airtest自动化测试技能

## 能力概述
本技能提供完整的Airtest自动化测试解决方案，包括：
- **Airtest核心操作**：文本点击、图像识别、滑动、截图等
- **ADB设备控制**：应用管理、设备操作、日志抓取
- **测试脚本生成**：根据自然语言描述自动生成Python测试脚本
- **脚本管理执行**：测试脚本的存储、执行和报告生成

## 执行流程

### 场景1：执行Airtest测试
当用户要求执行具体的UI测试时：
1. **解析需求**：提取测试目标、设备信息、操作步骤
2. **选择脚本**：在`tests/`目录查找匹配的测试脚本，或生成新脚本
3. **执行测试**：调用`scripts/test-runner.js`执行测试
4. **生成报告**：收集测试结果，生成HTML报告和截图

### 场景2：ADB设备控制
当用户需要控制Android设备时：
1. **解析命令**：识别ADB操作类型（安装、启动、日志等）
2. **执行ADB**：调用`scripts/adb-controller.js`执行对应命令
3. **返回结果**：显示命令执行结果和设备状态

### 场景3：生成测试脚本
当用户描述测试用例时：
1. **解析描述**：使用自然语言处理提取测试步骤
2. **选择模板**：根据测试类型选择合适的模板
3. **生成脚本**：调用`scripts/test-generator.js`生成Python脚本
4. **保存管理**：将脚本保存到`tests/`目录，并记录元数据

### 场景4：管理测试脚本
当用户需要查看或执行历史测试时：
1. **列出脚本**：显示`tests/`目录下的所有可用测试
2. **执行脚本**：选择并执行特定测试脚本
3. **查看报告**：展示历史测试报告和执行结果

## 可用命令格式

### Airtest操作
- `airtest click <target>` - 点击操作（支持文本/图片/坐标）
- `airtest swipe <from> <to>` - 滑动操作
- `airtest text <content>` - 输入文本
- `airtest snapshot <name>` - 截图
- `airtest wait <target>` - 等待元素出现
- `airtest exists <target>` - 检查元素是否存在

### ADB命令
- `adb install <apk_path>` - 安装应用
- `adb uninstall <package>` - 卸载应用
- `adb start <package>/<activity>` - 启动应用
- `adb stop <package>` - 停止应用
- `adb devices` - 列出设备
- `adb logcat <filter>` - 抓取日志

### 测试管理
- `test list` - 列出所有测试
- `test run <script_name>` - 执行测试
- `test generate <description>` - 生成测试脚本
- `test report <test_id>` - 查看报告

## 使用示例

```
用户: 帮我生成一个登录测试脚本
助手: [调用test-generator.js生成登录测试脚本]

用户: 执行ADB安装应用 /path/to/app.apk
助手: [调用adb-controller.js执行安装]

用户: 运行tests/auth/login-test.air.py
助手: [调用test-runner.js执行测试并生成报告]
```

## 依赖要求
- Python 3.6+
- Airtest库 (`pip install airtest`)
- Android SDK (ADB工具)
- Node.js 14+ (执行脚本)

## 配置说明
设备配置文件位于 `config/devices.json`，应用配置位于 `config/apps.json`。
环境变量配置位于 `config/env/` 目录。
