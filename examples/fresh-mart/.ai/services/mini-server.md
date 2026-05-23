# mini-server 服务档案

## 注册名 / 端口

`mini-server` / 8079（BFF）

## 角色

C 端小程序 BFF — JWT 鉴权 + 聚合下游服务数据。

## 核心职责

- JWT Token 校验（解出 memberId 透传）
- 商品详情聚合（基础信息 + 活动 + 我的可用券）
- 下单 / 支付 / 领券的请求转发

## 暴露接口

| 路径 | 积木 |
|------|------|
| POST `/api/mini/register` | member_register |
| GET `/api/mini/products` | product_browse |
| GET `/api/mini/product/{id}` | product_browse（聚合 3 服务） |
| POST `/api/mini/coupon/receive` | coupon_receive |
| POST `/api/mini/order` | order_create |
| POST `/api/mini/order/pay` | order_pay |

## 下游依赖

- product-service / promotion-service / order-service / member-service

## 关键约束

- 所有接口必须验证 JWT
- `X-Member-Id` 由网关层从 JWT 解出，向下游透传
