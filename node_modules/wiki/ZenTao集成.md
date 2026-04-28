# ZenTao 集成

## 连接信息

| 项目 | 内容 |
|------|------|
| 服务器 | http://192.168.0.28:9980 |
| 账号 | shidawei |
| 密码 | shidawei |
| Token | 335bfce2adddecff7b3097534e93cf3e |
| API 端点 | /api.php/v1 |

## 产品与迭代

| 项目 | ID |
|------|-----|
| 产品ID | 1 (数字乡村v1.1) |
| 迭代ID | 24 (邀请码专项) |

## Bug 统计

### 总体
| 状态 | 数量 |
|------|------|
| 总 Bug | 8,128 |
| 激活 | 221 |
| 已解决 | 8,128 |
| 解决率 | 97.4% |

### 邀请码专项迭代 (#24)
| 状态 | 数量 |
|------|------|
| 总 Bug | 12 |
| 激活 | 7 |
| 已解决 | 1 |
| 已关闭 | 4 |

## 已提交 Bug

- Bug ID: 9728, 9729

## API 使用

```bash
# 登录获取 token
curl -X POST "http://192.168.0.28:9980/api.php/v1/tokens" \
  -H "Content-Type: application/json" \
  -d '{"account":"shidawei","password":"shidawei"}'

# 查询 Bug 列表
curl "http://192.168.0.28:9980/api.php/v1/products/1/bugs" -H "Token: xxx"

# 创建 Bug
curl -X POST "http://192.168.0.28:9980/api.php/v1/products/1/bugs" \
  -H "Content-Type: application/json" -H "Token: xxx" \
  -d '{"title":"xxx", "severity":3, "pri":2, ...}'

# 更新 Bug
curl -X PUT "http://192.168.0.28:9980/api.php/v1/bugs/{id}" \
  -H "Content-Type: application/json" -H "Token: xxx" \
  -d '{"steps": "<p>内容</p>"}'
```

## 来源

- `MEMORY.md` - 长期记忆

---

*最后更新: 2026-04-27*
