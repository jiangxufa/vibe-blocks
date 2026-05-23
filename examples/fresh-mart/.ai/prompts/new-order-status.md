# 新增订单状态时的 checklist

当业务需要给订单引入新状态（如新增 SHIPPING 配送中、DELIVERED 已签收）时，按以下顺序操作：

## 1. 状态枚举

修改：

```
order-service/src/main/java/com/freshmart/entity/OrderStatus.java
.ai/references/enums.md  # 同步更新
```

## 2. 状态机校验

在 `OrderService` 与 `RefundService` 等编排逻辑中检查：

- 哪些方法依赖 `if (order.status == X)` 判断
- 是否需要新增状态流转规则

## 3. 现有积木更新

按以下顺序检查（不要漏）：

- [ ] `order_create.md`：创建后是否会进入新状态？
- [ ] `order_pay.md`：支付成功是否变成新状态？
- [ ] `order_refund.md`：退款判断 `status=PAID` 是否要扩展？
- [ ] 各积木的 Mermaid 图 `OrderStatus` 标注

## 4. 新积木

如果新状态有独立的业务流程（如配送），创建新积木：

```bash
vibe-blocks new order_ship --group 订单 --name 订单发货
```

## 5. 数据库迁移

```sql
-- 注意 ENUM 字段如果已用 VARCHAR 存储，无需改表结构
-- 如果用 ENUM 类型，需要 ALTER TABLE
```

## 6. 测试

- [ ] 单元测试覆盖新状态流转
- [ ] 旧订单数据兼容（已存在的订单状态值不应失效）
- [ ] 前端兼容（mini-server BFF 是否需要状态文案适配）

## 7. 提交规范

```
feat: 订单新增 SHIPPING 状态

- 修改 OrderStatus 枚举
- 更新 order_create / order_pay 积木
- 新增 order_ship 积木
- 同步 .ai/references/enums.md
```
