# 平台支持

本项目的核心资产是 `skills/`、`commands/` 和 `hooks/`。不同宿主平台的接入方式不同，下面给出当前明确支持的路径。

| 平台 | 自动注入 | 手动命令 | 安装入口 | 验证方式 |
|------|---------|---------|---------|---------|
| Claude Code | 支持 | 支持 | `.claude-plugin/` | `tests/validate.ps1` |
| Cursor | 支持元数据与 hook | 支持 | `.cursor-plugin/` | `tests/validate.ps1` |
| Codex | 不依赖插件壳 | 视宿主能力而定 | `.codex/INSTALL.md` | 按文档自检 |
| OpenCode | 不依赖插件壳 | 视宿主能力而定 | `.opencode/INSTALL.md` | 按文档自检 |
| 其他宿主 | 手动集成 | 视宿主能力而定 | 直接复用 `skills/` 和 `commands/` | 手动检查 |

## Windows

- `hooks/run-hook.cmd` 会优先执行 `hooks/session-start.ps1`
- 不再要求用户额外安装 Git Bash / WSL
- `bash` / `sh` 仅作为兜底路径保留

## macOS / Linux

- 使用 `hooks/session-start`
- 需要可用的 `bash` 或 `sh`

## 命令层

- 仓库提供 `commands/*.md` 手动入口
- 支持 Markdown slash commands 的宿主可直接使用
- 不支持命令目录的宿主，可直接读取同名文件中的指令内容

## 验证建议

Windows：

```powershell
powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File tests/validate.ps1
```

验证脚本会检查：
- JSON 配置有效性
- hook 文件是否齐全
- PowerShell hook 与 `run-hook.cmd` 的 smoke test
- skills / agents / commands frontmatter 完整性
- README 与平台文档中的本地链接是否存在
