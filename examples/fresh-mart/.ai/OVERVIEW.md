# fresh-mart 项目全貌

## 这个项目是什么

一个生鲜电商示例平台。会员可以浏览商品、下单、支付、退款，运营可以发券、办活动。本项目是 **vibe-blocks 的官方实战示例**，所有代码为伪代码。

## 技术栈

- 语言：Java 11
- 框架：Spring Boot 2.7 + Spring Cloud
- 服务通信：OpenFeign（同步）+ MQ（异步）
- 数据库：MySQL（JPA/Hibernate）
- 缓存：Redis
- 第三方：微信支付

## 服务拓扑

```
┌─────────────────────────────────────────────────────┐
│                    入口层（BFF）                      │
│        admin-server         mini-server             │
└──────────────────────┬──────────────────────────────┘
                       │ Feign
┌──────────────────────▼──────────────────────────────┐
│                   核心业务层                          │
│   member-service   order-service                    │
│   product-service  promotion-service                │
└─────────────────────────────────────────────────────┘
        │                                  │
   MySQL / Redis                  MQ / 微信支付
```

## 模块职责速查

| 模块 | 类型 | 职责 |
|------|------|------|
| admin-server | BFF | 运营后台：发券、办活动、退款、会员管理 |
| mini-server | BFF | C 端小程序：浏览、下单、支付、领券 |
| member-service | 核心 | 会员、积分、等级、注册 |
| order-service | 核心 | 订单、支付状态、退款 |
| product-service | 核心 | 商品、库存（available/locked/sold 三段） |
| promotion-service | 核心 | 营销活动、优惠券（模板 + 用户券）、拼团 |

## 目录结构约定

```
{module}/src/main/java/com/freshmart/
├── controller/  # REST 入口，参数包装与权限注解
├── service/     # 业务编排，可以调下游服务
├── client/      # Feign 接口（@FeignClient）
├── entity/      # JPA 实体
└── repository/  # 数据访问层
```

## 跨服务数据归属

- **会员/积分**：member-service 是唯一写入方
- **库存**：product-service 是唯一写入方（三段：available / locked / sold）
- **券模板/用户券**：promotion-service 是唯一写入方
- **订单**：order-service 是唯一写入方
- BFF 层（admin-server / mini-server）**只做编排，不直接操作下游数据库**

## 认证体系

- admin-server：Apache Shiro（`@RequiresPermissions("xxx:add")`）
- mini-server：JWT Token，header 透传 `X-Member-Id`
- 服务间调用：固定 token 标识调用方
