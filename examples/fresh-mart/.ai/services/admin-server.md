# admin-server 服务档案

## 注册名 / 端口

`admin-server` / 8080（BFF）

## 角色

运营后台 BFF — 权限控制 + 多服务聚合，**不直接操作下游数据库**。

## 核心职责

- Shiro 鉴权（细粒度的 `@RequiresPermissions`）
- 聚合 member / order / promotion 多服务数据给运营页面
- 触发运营操作：建券、办活动、退款、会员管理

## 暴露接口（前端调用）

| 路径 | 权限 | 积木 |
|------|------|------|
| POST `/sys/coupon/template` | coupon:add | coupon_create |
| POST `/sys/activity` | activity:add | （待扩展） |
| POST `/sys/order/refund` | order:refund | order_refund |
| GET `/sys/member/{id}/profile` | member:view | （聚合查询，无独立积木） |

## 下游依赖

- promotion-service / order-service / member-service / product-service

## 关键约束

- **不写数据库**：所有数据操作必须通过下游 Feign 调用
- **必须鉴权**：每个接口都要有 `@RequiresPermissions`
