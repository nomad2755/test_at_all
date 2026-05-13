# ZenTao Bug API - 完整字段参考

## 创建 Bug API

```
POST /api.php/v1/bugs
Headers:
  Token: {token}
  Content-Type: application/json
  Zentao-Version: 22.4
```

## 必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `product` | int | 产品 ID（数字乡村v1.1 = 1） |
| `title` | string | Bug 标题，建议格式：【优先级】模块-问题描述 |
| `steps` | string | **HTML 格式**，见下方模板 |
| `severity` | int | 严重程度 1-5 |
| `pri` | int | 优先级 1-4 |
| `type` | string | Bug 类型 |
| `openedBuild` | string | 影响版本，传 `"trunk"` |

## severity（严重程度）

| 值 | 含义 |
|----|------|
| 1 | 致命 - 系统崩溃、死机、无法继续测试 |
| 2 | 严重 - 功能未实现或严重偏差，影响主要流程 |
| 3 | 一般 - 功能缺陷，但不影响主要流程 |
| 4 | 轻微 - 界面、提示文案等小问题 |
| 5 | 建议 - 优化建议、体验问题 |

## pri（优先级）

| 值 | 含义 |
|----|------|
| 1 | 紧急 - 必须立刻修复 |
| 2 | 高 - 本版本必须修复 |
| 3 | 中 - 正常流程修复 |
| 4 | 低 - 有时间就修复 |

## type（Bug类型）

| 值 | 含义 |
|----|------|
| `codeerror` | 代码错误 |
| `interface` | 界面优化 |
| `function` | 功能缺陷 |
| `performance` | 性能问题 |
| `others` | 其他 |

## steps HTML 模板

```html
<p>【环境】</p>
<p>- 测试地址：https://whhnhy.com:8910</p>
<p>- 浏览器：Chrome latest</p>
<p>- APP版本：v1.0</p>
<p>【账号密码】</p>
<p>- 用户名：tester</p>
<p>- 密码：test123</p>
<p>【前置条件】</p>
<p>1. 已登录系统</p>
<p>【操作步骤】</p>
<p>1. 访问首页</p>
<p>2. 点击「测试」菜单</p>
<p>【期望结果】</p>
<p>1. 页面正常加载</p>
<p>2. 无控制台报错</p>
<p>【实际结果】</p>
<p>1. 页面加载成功</p>
<p>2. 控制台报 JS 错误</p>
<p>【附截图】</p>
<p>暂无</p>
```

**关键点：**
- 用 `<p>` 标签包裹每行内容
- 各段落标题用【】包裹
- steps 字段是**字符串**，不是 JSON 对象数组

## 可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `module` | int | 模块 ID（默认 0） |
| `assignedTo` | string | 指派人账号 |
| `deadline` | string | 截止日期 YYYY-MM-DD |
| `keywords` | string | 关键词标签 |
| `mailto` | array | 抄送用户列表 |

## 产品 ID 参考

| 产品 | ID |
|------|----|
| 数字乡村v1.1 | 1 |
| 个人数字空间 | 2 |
