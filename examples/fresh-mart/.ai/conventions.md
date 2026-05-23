# 编码与积木维护约定

## 积木维护规则

每次修改业务流程相关代码时，必须同步更新对应积木：

1. **找到受影响的积木**：根据修改文件路径在 `.ai/blocks/*.md` 中的「锚点」字段反查
2. **更新节点逻辑**：处理步骤变了就改
3. **更新 Mermaid 图**：调用链变了就改
4. **追加变更记录**：一行说明改了什么 + MR 号
5. **如果是新流程**：用 `vibe-blocks new <id>` 创建新积木

不需要更新积木的情况：纯重构、不改流程语义的 bug fix、仅改日志或注释。

## 积木粒度标准

一个积木 = 一条完整的业务流程（从触发到响应）

- ✅ 创建订单、用户注册、领取优惠券、订单退款、订单超时取消
- ❌ "参数校验"（太细）、"订单系统"（太粗）

## 代码分层约定

```
Controller（入口） → Service（业务编排） → Repository（数据访问）
       ↓ Feign
下游 Controller → Service → Repository
```

- Controller 只做参数接收与权限校验，不写业务
- Service 负责业务编排，可以调 Feign Client
- BFF 层只做编排聚合，**禁止直接操作下游数据库**

## 服务间通信约定

- 同步调用：OpenFeign（HTTP/REST）
- 异步通信：MQ
- Feign 接口定义在调用方的 `client/` 包内
- 跨服务响应统一用 `BaseResponse` / `BaseResponse<T>` 包装
- Feign 调用后必须 `checkResponse()` 校验后再用

## 错误处理约定

- 业务异常统一抛 `ServiceException`
- Feign 调用失败 `checkResponse()` 自动转 `ServiceException`
- Controller 不捕获异常，全局异常处理器统一处理

## 命名约定

- Feign Client：`XxxClient`（如 `MemberClient`）
- DTO 请求：`XxxRequest`
- DTO 响应：`XxxDTO` / `XxxResponse`
- 服务类：`XxxService`
- 控制器：`XxxController`
- VO（聚合给前端）：`XxxVO`

## 不要做的事

- 不要在 BFF 层直接连下游数据库
- 不要跳过 `checkResponse()` 直接用 Feign 返回值
- 不要硬编码环境相关配置
- 不要创建积木后忘了在 `_index.md` 注册（用 `vibe-blocks new` 自动注册）

## 异步调用规范

异步消息（MQ）必须在 Mermaid 图中：
1. 声明参与者：`participant MQ as MQ`
2. 用 `rect rgb(255, 230, 150)` 包裹发送行（橙色高亮）

## 分布式事务边界

本项目**不**使用 XA / Saga 框架，跨服务一致性通过：

- **try-compensate 模式**：下单时若优惠券锁定失败，主动调 `releaseStock` 补偿
- **延时消息 + 状态查询**：30 分钟未支付的订单由 MQ 触发取消并释放资源
- **幂等设计**：所有跨服务写操作支持重试（如支付回调按 prepayId 幂等）
