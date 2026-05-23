# member-service 服务档案

## 注册名 / 端口

`member-service` / 8081

## 核心职责

- 会员注册、等级、积分
- 等级自动升级（积分变动触发）
- 积分记录（points_log 全量留痕）

## 暴露接口

| 路径 | 调用方 | 积木 |
|------|--------|------|
| POST `/v1/member/register` | mini-server | member_register |
| GET `/v1/member/{id}` | order-service / admin-server | order_create / 多处 |
| POST `/v1/member/points/add` | order-service（异步消费 order.paid 后） | order_pay / member_level_upgrade |
| POST `/v1/member/points/deduct` | order-service | order_pay / order_refund |
| POST `/v1/member/points/refund` | order-service | order_refund |

## 数据所有权

| 表 | 说明 |
|------|------|
| `member` | 会员主表 |
| `points_log` | 积分流水（全量留痕，不可删） |
| `member_level` | 等级配置表 |

## 消息事件（发出）

| Topic | 时机 | 谁消费 |
|-------|------|--------|
| `member.registered` | 注册成功 | promotion-service（发新人券） |
| `member.level.upgraded` | 等级变化 | notification-service（待实现，发通知） |

## 消息事件（消费）

| Topic | 处理 |
|-------|------|
| `order.paid` | 调 `addPoints` 1% 返积分（触发等级升级） |
