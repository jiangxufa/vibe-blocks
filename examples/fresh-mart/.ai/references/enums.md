# 业务枚举速查表

## 订单状态 OrderStatus

| 值 | 说明 | 流转触发 |
|----|------|----------|
| `PENDING_LOCK` | 待锁定（短暂中间态） | 创建订单后 |
| `PENDING_PAY` | 待支付 | 库存与券锁定成功后 |
| `PAID` | 已支付 | 微信回调成功 |
| `CANCELLED` | 已取消 | 用户主动 / 30 分钟超时 |
| `FAILED` | 创建失败 | 库存或券锁定失败 |
| `REFUNDED` | 已退款 | 退款成功 |

## 支付状态 PaymentStatus

| 值 | 说明 |
|----|------|
| `PROCESSING` | 微信预下单后，等待用户支付 |
| `SUCCESS` | 支付成功（回调验证通过） |
| `FAILED` | 支付失败 |
| `REFUNDED` | 已退款 |

## 退款状态 RefundStatus

| 值 | 说明 |
|----|------|
| `PROCESSING` | 退款受理中（微信侧处理） |
| `SUCCESS` | 退款完成 |
| `FAILED` | 微信退款失败 |

## 会员等级 MemberLevel

| 值 | 积分门槛 | 权益 |
|----|----------|------|
| `NORMAL` | 0+ | - |
| `SILVER` | 1000+ | 9 折 |
| `GOLD` | 5000+ | 8.5 折 |
| `DIAMOND` | 20000+ | 8 折 + 专属客服 |

## 优惠券状态

| 值 | 说明 |
|----|------|
| `UNUSED` | 未使用 |
| `LOCKED` | 已下单锁定（lockedOrderNo 关联） |
| `USED` | 已核销 |
| `EXPIRED` | 已过期（每日定时任务批量更新） |

## 优惠券模板状态 CouponStatus

| 值 | 说明 |
|----|------|
| `PENDING` | 待发放 |
| `ACTIVE` | 发放中 |
| `ENDED` | 已结束 |

## 积分变动类型 PointsLog.type

| 值 | 含义 |
|----|------|
| `earn` | 订单完成 1% 返积分 |
| `deduct` | 下单使用积分抵扣 |
| `refund` | 退款时退还已扣积分 |
