# order-service 服务档案

## 注册名

`order-service`（Spring Cloud Eureka）

## 端口

8082

## 核心职责

- 订单生命周期管理（创建、支付、取消、退款）
- 跨多服务编排（库存、券、积分）
- 支付回调幂等处理
- 订单超时自动取消（基于 MQ 延时消息）

## 暴露接口（Feign 调用方）

| 路径 | 方法 | 调用方 | 关联积木 |
|------|------|--------|----------|
| `/v1/order/create` | POST | mini-server | order_create |
| `/v1/order/pay` | POST | mini-server | order_pay |
| `/v1/order/pay/callback` | POST | 微信支付 | order_pay |
| `/v1/order/refund` | POST | admin-server | order_refund |
| `/v1/order/{orderNo}` | GET | mini-server / admin-server | - |
| `/v1/order/by-member/{id}` | GET | admin-server | - |

## 上游依赖（被谁调）

- `mini-server`：下单、支付、查订单
- `admin-server`：退款、查会员订单
- 微信支付：支付回调

## 下游依赖（调谁）

- `member-service`：校验会员、扣/退积分
- `product-service`：锁/扣/退库存
- `promotion-service`：锁/核销/退优惠券
- `WxPayClient`：发起支付、退款

## 数据所有权

| 表 | 说明 |
|------|------|
| `order` | 订单主表 |
| `order_item` | 订单明细 |
| `payment` | 支付单 |
| `refund` | 退款单 |

## 消息事件（发出）

| Topic | 何时发 | 谁消费 |
|-------|--------|--------|
| `order.pay.timeout` | 创单后延时 30 分钟 | order-service 自己（取消未支付订单） |
| `order.paid` | 支付回调成功后 | member-service（返积分） |
| `order.refunded` | 退款成功后 | notification-service（待实现，发通知） |

## 消息事件（消费）

| Topic | 处理逻辑 |
|-------|----------|
| `order.pay.timeout` | `OrderService#cancelIfTimeout` 取消未支付订单 |
