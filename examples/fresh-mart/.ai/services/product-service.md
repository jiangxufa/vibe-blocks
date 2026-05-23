# product-service 服务档案

## 注册名 / 端口

`product-service` / 8083

## 核心职责

- 商品基础信息维护
- 库存三段管理：`available`（可售）/ `locked`（锁定）/ `sold`（已售）
- 库存流转：lock → deduct（支付）/ release（取消）/ refund（退款）

## 暴露接口

| 路径 | 调用方 | 积木 |
|------|--------|------|
| GET `/v1/product/list` | mini-server | product_browse |
| GET `/v1/product/{id}` | mini-server | product_browse |
| POST `/v1/product/batch` | order-service | order_create |
| POST `/v1/product/stock/lock` | order-service | order_create |
| POST `/v1/product/stock/release` | order-service | order_create 异常路径 |
| POST `/v1/product/stock/deduct` | order-service | order_pay |
| POST `/v1/product/stock/refund` | order-service | order_refund |

## 数据所有权

| 表 | 说明 |
|------|------|
| `product` | 商品主表 |
| `stock` | 库存（available/locked/sold 三段） |
| `stock_lock` | 锁定记录（含 30 分钟过期时间） |
| `category` | 商品分类 |

## 关键约束

- **不允许 `available < 0`**：lockStock 必须用 `findByProductIdForUpdate` 行锁
- **stock_lock 30 分钟超时**：定时任务扫描过期记录自动释放
