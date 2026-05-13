# Bug 截图管理

## 访问地址（内网）

**截图列表 / 文件访问：**
- `http://192.168.0.68:8099/screenshots`
- 直接访问文件：`http://192.168.0.68:8099/screenshots/文件名.png`

## 上传截图

```bash
python3 /root/.openclaw/workspace/scripts/bug_screenshot_manager.py upload <图片路径> [描述]
```

示例：
```bash
python3 /root/.openclaw/workspace/scripts/bug_screenshot_manager.py upload /tmp/bug1.png "登录页面崩溃"
```

## 其他命令

```bash
# 列出所有截图
python3 /root/.openclaw/workspace/scripts/bug_screenshot_manager.py list

# 获取指定文件 URL
python3 /root/.openclaw/workspace/scripts/bug_screenshot_manager.py url 文件名.png

# 删除截图
python3 /root/.openclaw/workspace/scripts/bug_screenshot_manager.py delete 文件名.png
```

## 目录结构

- 本地存储：`/root/.openclaw/workspace/bug_screenshots/`
- 元数据：`/root/.openclaw/workspace/bug_screenshots/metadata.json`
