# 跨服务数据归属

每个数据实体只能由**唯一**服务写入，避免脏写。

| 数据 | 归属服务 | 其他服务怎么用 |
|------|----------|------|
| 会员基础信息 | member-service | Feign GET `/v1/member/{id}` |
| 会员积分 | member-service | Feign POST `/v1/member/points/*` |
| 会员等级 | member-service | 同上（升级由内部触发） |
| 商品信息 | product-service | Feign GET `/v1/product/*` |
| 库存 | product-service | Feign POST `/v1/product/stock/*` |
| 券模板 | promotion-service | Feign POST `/v1/promotion/coupon/template` |
| 用户券 | promotion-service | Feign POST `/v1/promotion/coupon/*` |
| 订单 | order-service | Feign POST `/v1/order/*` |
| 支付/退款单 | order-service | 同上 |

## 反例（禁止做的）

- ❌ admin-server 直接 SQL 改 `member` 表
- ❌ order-service 直接更新 `coupon` 表（必须调 promotion-service）
- ❌ 跨服务用同一个 DB（即使物理上同一个实例，逻辑上必须按服务隔离）

## 正例

- ✅ admin-server 改会员等级 → Feign 调 member-service 提供的接口（如果没有，先在 member-service 加）
- ✅ order_pay 扣库存 → 调 product-service `stock/deduct`
