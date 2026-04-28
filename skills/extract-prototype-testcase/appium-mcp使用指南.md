# Appium MCP 使用指南

## 概述

Appium MCP 是一个基于 Model Context Protocol (MCP) 的 Appium 自动化测试服务器连接器，允许 AI 助手（如 Claude）通过 MCP 协议直接与 Appium 服务器通信，实现移动端应用的自动化测试控制。

**官方仓库**: https://github.com/appium/appium-mcp

---

## 环境要求

| 依赖 | 版本要求 | 说明 |
|------|---------|------|
| Node.js | ≥ 18.0.0 | MCP 服务器运行环境 |
| npm / npx | 最新版 | 包管理器 |
| Appium Server | ≥ 2.0.0 | Appium 服务端 |
| Appium 客户端驱动 | 根据需求 | 如 `appium-uiautomator2-driver`、`appium-xcuitest-driver` 等 |

---

## 安装步骤

### 方式一：直接使用 npx（推荐，无需全局安装）

```bash
npx appium-mcp
```

### 方式二：全局安装

```bash
npm install -g appium-mcp
```

### 方式三：在项目中安装

```bash
npm install appium-mcp
```

---

## Appium 服务器启动

### 1. 启动 Appium Server

```bash
# 全局安装 appium（如果尚未安装）
npm install -g appium

# 启动 Appium 服务（默认端口 4723）
appium

# 或指定端口
appium --port 4724

# 或使用配置文件启动
appium --config appium.config.json
```

### 2. 启动 Appium Server（远程设备）

```bash
# 连接远程 Selenium Grid 或云设备
appium --host remote-host.com --port 4723

# 连接 BrowserStack / Sauce Labs 等云平台
appium --hub https://hub-cloud.browserstack.com/wd/hub
```

---

## Claude Desktop 配置

### 配置 MCP 服务器

编辑 Claude Desktop 配置文件：
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

### 基础配置（本地 Appium）

```json
{
  "mcpServers": {
    "appium": {
      "command": "npx",
      "args": ["appium-mcp"],
      "env": {
        "APPIUM_HOST": "localhost",
        "APPIUM_PORT": "4723"
      }
    }
  }
}
```

### 使用全局安装的 appium-mcp

```json
{
  "mcpServers": {
    "appium": {
      "command": "appium-mcp",
      "env": {
        "APPIUM_HOST": "localhost",
        "APPIUM_PORT": "4723"
      }
    }
  }
}
```

### 远程设备配置

```json
{
  "mcpServers": {
    "appium": {
      "command": "npx",
      "args": ["appium-mcp"],
      "env": {
        "APPIUM_HOST": "your-remote-host.com",
        "APPIUM_PORT": "4723",
        "APPIUM_USERNAME": "your-username",
        "APPIUM_ACCESS_KEY": "your-access-key"
      }
    }
  }
}
```

### iOS 专项配置（XCUI）

```json
{
  "mcpServers": {
    "appium": {
      "command": "npx",
      "args": ["appium-mcp"],
      "env": {
        "APPIUM_HOST": "localhost",
        "APPIUM_PORT": "4723",
        "APPIUM_PLATFORM": "ios",
        "XCUITEST_BUNDLE_ID": "com.example.yourapp"
      }
    }
  }
}
```

---

## 可用 MCP 工具

Appium MCP 提供以下核心工具：

| 工具名称 | 功能 |
|---------|------|
| `appium_start_session` | 启动新的 Appium 会话（连接设备+启动 App） |
| `appium_end_session` | 结束当前 Appium 会话 |
| `appium_find_element` | 查找单个元素（支持多种定位策略） |
| `appium_find_elements` | 查找多个元素 |
| `appium_click` | 点击元素 |
| `appium_send_keys` | 向输入框输入文本 |
| `appium_get_text` | 获取元素文本 |
| `appium_get_attribute` | 获取元素属性 |
| `appium_screenshot` | 截图 |
| `appium_execute_script` | 执行 JavaScript 命令 |
| `appium_swipe` | 滑动操作 |
| `appium_scroll` | 滚动操作 |
| `appium_get_page_source` | 获取页面 XML 源码 |
| `appium_get_clipboard` | 获取剪贴板内容 |
| `appium_set_clipboard` | 设置剪贴板内容 |
| `appium_is_element_displayed` | 检查元素是否可见 |

### 元素定位策略

| 策略 | 示例 |
|------|------|
| accessibility_id | `"accessibility_id:my-button"` |
| xpath | `"xpath://android.widget.Button[@text='确认']"` |
| id | `"id:com.example:id/btn_confirm"` |
| class name | `"class_name:android.widget.Button"` |
| uiAutomator | `"uiAutomator:new UiSelector().text('确认')"` |

---

## 使用示例

### 在 Claude Code 中使用

```
打开手机上的淘宝App，搜索"酱板鸭"，截图给我看
```

Claude 会自动：
1. 通过 `appium_start_session` 启动 Appium 会话
2. 启动目标 App（淘宝）
3. 执行搜索操作
4. 使用 `appium_screenshot` 截图返回给你

### 自动化测试流程

```
1. 启动会话 → appium_start_session
2. 等待元素 → appium_find_element
3. 执行操作 → appium_click / appium_send_keys
4. 验证结果 → appium_screenshot / appium_get_text
5. 结束会话 → appium_end_session
```

---

## 常见问题

### Q1: npx 执行慢或失败
```bash
# 先全局安装 appium-mcp
npm install -g appium-mcp

# 然后直接用命令
appium-mcp
```

### Q2: 连接设备失败
```bash
# 检查设备连接状态
adb devices  # Android
# 或
 instruments -s devices  # iOS

# 确保 Appium Server 已启动
appium
```

### Q3: 权限错误（iOS）
- 需要配置 WebDriverAgent（Xcode 项目签名）
- 或使用真机调试证书

### Q4: Windows 上找不到 npx
确保 Node.js 安装在 PATH 中，或使用完整路径：
```json
{
  "mcpServers": {
    "appium": {
      "command": "C:/Program Files/nodejs/npx.cmd",
      "args": ["appium-mcp"]
    }
  }
}
```

### Q5: 多设备并发
MCP 目前不支持多设备并发，如需并发测试请启动多个 Claude 实例。

---

## 与 Appium 传统写法的对比

| 方面 | 传统 Appium | Appium MCP |
|------|------------|-----------|
| 编程语言 | Java/Python/JavaScript | 自然语言（中文/英文） |
| 代码量 | 大量代码 | 几乎为零 |
| 定位元素 | 手动编写定位器 | AI 自动识别 |
| 断言验证 | 手动编写断言 | AI 辅助判断 |
| 适用场景 | 复杂自动化工程 | 快速探索、简单测试 |

---

## 相关资源

| 资源 | 链接 |
|------|------|
| 官方文档 | https://github.com/appium/appium-mcp |
| Appium 官网 | https://appium.io |
| Appium 文档 | https://appium.io/docs/en/latest/ |
| MCP 协议 | https://modelcontextprotocol.io |
