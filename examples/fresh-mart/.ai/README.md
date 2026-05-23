# AI 知识库 — fresh-mart

本目录由 **vibe-blocks** 管理，是 AI 编码（vibe coding）的全部上下文来源。

## 目录结构

```
.ai/
├── OVERVIEW.md         # 项目全貌
├── conventions.md      # 编码约定（强制）
├── blocks/             # 业务流程积木（8 个）
│   ├── _index.md
│   ├── _template.md
│   ├── member_register.md
│   ├── product_browse.md
│   ├── coupon_create.md
│   ├── coupon_receive.md
│   ├── member_level_upgrade.md
│   ├── order_create.md      ⭐ 复杂
│   ├── order_pay.md         ⭐⭐ 复杂
│   └── order_refund.md      ⭐⭐⭐ 最复杂
├── services/           # 6 份服务档案
├── references/         # 枚举、跨服务数据归属
├── decisions/          # ADR-001 BFF / ADR-002 分布式事务
├── prompts/            # 常见任务工作流（如新增订单状态）
└── changelog/          # 知识库变更日志（待填）
```

## 怎么用

```bash
# 浏览可视化网页（一键生成）
vibe-blocks build --output blocks-view.html
open blocks-view.html

# 创建新积木
vibe-blocks new order_ship --group 订单 --name 订单发货

# 刷新顶层 CLAUDE.md
vibe-blocks claude-md --path ..
```
