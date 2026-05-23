# CLAUDE.md — fresh-mart

> 由 [vibe-blocks](https://github.com/jiangxufa/vibe-blocks) 生成 / 维护 · 最后更新：2026-05-22

## 项目概述

_一句话描述项目是什么，建议手动补充。_

## 技术栈

- Java + Maven

## AI 行为准则

### 先思考再编码
- 实施前明确陈述假设；不确定就问清楚
- 多种解释全部呈现，不私下选择

### 简约优先
- 只写解决问题所需的最小代码
- 不为不可能的情况写错误处理

### 手术式变更
- 只触碰必需之物，不"改进"相邻代码
- 与现有风格保持一致

### 信任锚点
- 修改业务流程相关代码后，必须同步更新对应的 `.ai/blocks/*.md` 积木
- 通过 `--anchor` 注释或 `锚点` 字段定位代码

## 业务流程积木索引

积木总数：**8**（stable=8, draft=0, deprecated=0）

### 会员

- ✅ [`member_register`](.ai/blocks/member_register.md) — 会员注册（POST /api/mini/register）
- ✅ [`member_level_upgrade`](.ai/blocks/member_level_upgrade.md) — 会员等级自动升级（内部触发（订单完成返积分时检查））

### 商品

- ✅ [`product_browse`](.ai/blocks/product_browse.md) — 商品列表/详情浏览（GET /api/mini/products, GET /api/mini/product/{id}）

### 营销

- ✅ [`coupon_create`](.ai/blocks/coupon_create.md) — 创建优惠券模板（POST /sys/coupon/template）
- ✅ [`coupon_receive`](.ai/blocks/coupon_receive.md) — 用户领取优惠券（POST /api/mini/coupon/receive）

### 订单 ⭐ 核心复杂流程

- ✅ [`order_create`](.ai/blocks/order_create.md) — 创建订单（下单）（POST /api/mini/order）
- ✅ [`order_pay`](.ai/blocks/order_pay.md) — 订单支付（POST /api/mini/order/pay + 微信支付回调 POST /v1/order/pay/callback）
- ✅ [`order_refund`](.ai/blocks/order_refund.md) — 订单退款（POST /sys/order/refund）

## 知识库目录

详细的业务积木、服务档案等文档位于 `.ai/`：

- `.ai/OVERVIEW.md` — 项目全景概述
- `.ai/conventions.md` — 编码与积木维护约定
- `.ai/blocks/` — 业务流程积木（每个文件 = 一条业务流程）
- `.ai/services/` — 服务档案（每个服务的接口、依赖、职责）
- `.ai/references/` — 参考速查（枚举、常量、配置）
- `.ai/decisions/` — 架构决策记录（ADR）
- `.ai/prompts/` — 常见任务的 AI 工作流模板

## 工作流提示

- **开发新功能**：先看 `.ai/blocks/_template.md`，运行 `vibe-blocks new <id>` 创建积木
- **理解已有功能**：先读积木的流程图与节点逻辑，再看代码
- **修改流程**：必须同步更新积木的「节点逻辑」「mermaid 图」「变更记录」
- **生成可视化**：运行 `vibe-blocks build`，浏览器打开 `project-blocks.html`
- **刷新本文件**：运行 `vibe-blocks claude-md` 重新扫描项目并更新

## 不要做的事

- 不要绕过积木直接修改业务流程代码
- 不要在积木中编造代码锚点（必须真实指向某个方法/文件）
- 不要把粒度做得太细（一个积木 = 一条完整业务流程）
