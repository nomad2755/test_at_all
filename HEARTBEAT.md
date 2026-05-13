# HEARTBEAT.md

# Keep this file empty (or with only comments) to skip heartbeat API calls.

# Add tasks below when you want the agent to check something periodically.

## 定时任务健康监测
每次心跳时检查 cron jobs 状态：
- 检查4个定时任务 (urgent_bug_alerter, daily_bug_report x2, daily_creator_bug_report)
- 如果发现 consecutiveErrors > 0 或 lastRunStatus = error，立即在当前会话报告
- 检查日志文件是否有异常：logs/urgent_bug_alerter.log, logs/creator_bug_report.log
- 上次检查时间: 记录在 heartbeat-state.json