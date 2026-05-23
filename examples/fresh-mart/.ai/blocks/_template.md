---
id: {flow_id}
name: {流程中文名}
owner: {负责团队}
status: draft
last_modified: {YYYY-MM-DD}
services: [{参与的服务列表}]
triggers: {触发方式}
related_mr: {相关MR}
---

## 流程总览

```mermaid
sequenceDiagram
    participant C as 触发方
    participant A as 服务A
    participant DB as MySQL

    C->>A: 请求
    A->>DB: 数据操作
    A-->>C: 响应
```

## 节点逻辑

### {服务名} — {角色描述}

**入口**：`ClassName#methodName`
**锚点**：`{模块}/src/main/java/{path}#{method}`

处理步骤：
1.

**写表**：
**发事件**：

## 异常路径

| 场景 | 处理 | 返回 |
|------|------|------|
|      |      |      |

## 变更记录

- {YYYY-MM-DD}: 初始创建
