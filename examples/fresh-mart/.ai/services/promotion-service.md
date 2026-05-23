# promotion-service 服务档案

## 注册名 / 端口

`promotion-service` / 8084

## 核心职责

- 优惠券模板管理（运营创建）
- 用户券领取（防超发 + 单人限领）
- 券生命周期：UNUSED → LOCKED → USED / 释放回 UNUSED
- 营销活动管理（待扩展：满减、拼团）

## 暴露接口

| 路径 | 调用方 | 积木 |
|------|--------|------|
| POST `/v1/promotion/coupon/template` | admin-server | coupon_create |
| POST `/v1/promotion/coupon/receive` | mini-server | coupon_receive |
| POST `/v1/promotion/coupon/lock` | order-service | order_create |
| POST `/v1/promotion/coupon/use` | order-service | order_pay |
| POST `/v1/promotion/coupon/release` | order-service | order_create 异常 |
| POST `/v1/promotion/coupon/refund` | order-service | order_refund |
| POST `/v1/promotion/activity` | admin-server | （待扩展） |

## 数据所有权

| 表 | 说明 |
|------|------|
| `coupon_template` | 券模板（含 remain_count 防超发） |
| `coupon` | 用户券（status: UNUSED/LOCKED/USED/EXPIRED） |
| `activity` | 营销活动 |

## 消息事件（发出）

| Topic | 时机 |
|-------|------|
| `coupon.template.created` | 运营创建券模板（用于通知/触达） |

## 消息事件（消费）

| Topic | 处理 |
|-------|------|
| `member.registered` | 给新用户发新人券 |
