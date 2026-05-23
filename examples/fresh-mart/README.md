# fresh-mart — 生鲜电商微服务示例

> **vibe-blocks 完整实战示例**：一个 6 服务的生鲜电商平台，所有代码为**伪代码**形式，重点演示 `.ai/blocks/` 积木如何描述真实的跨服务调用。

## 这是什么

这是 vibe-blocks 的官方参考案例，模拟一个生鲜电商业务系统：

- 6 个微服务（2 个 BFF + 4 个核心服务）
- 8 个业务积木（其中 3 个跨 4+ 服务的复杂流程）
- 完整的 `.ai/` 知识库（CLAUDE.md / OVERVIEW / 服务档案 / 枚举速查 / ADR）
- 用 `vibe-blocks build` 一键可看可视化网页

## 服务拓扑

```
┌─────────────────────────────────────────────────────┐
│                   入口层（BFF）                       │
│        admin-server         mini-server             │
└──────────────────────┬──────────────────────────────┘
                       │ Feign
┌──────────────────────▼──────────────────────────────┐
│                   核心业务层                          │
│   member-service   order-service                    │
│   product-service  promotion-service                │
└──────────────────────┬──────────────────────────────┘
                       │
        MySQL / Redis / MQ / 微信支付
```

## 怎么用

```bash
# 1. 看可视化（已 build 好）
open .ai/blocks-view.html  # 或 vibe-blocks build 后查看

# 2. 重新生成可视化
cd /path/to/fresh-mart
vibe-blocks build --blocks-dir .ai/blocks --output .ai/blocks-view.html

# 3. 重新刷新 CLAUDE.md
vibe-blocks claude-md
```

## 积木列表

| ID | 复杂度 | 涉及服务 |
|---|---|---|
| `member_register` | 🟢 简单 | mini-server, member-service |
| `product_browse` | 🟢 简单 | mini-server, product-service |
| `coupon_create` | 🟡 中等 | admin-server, promotion-service |
| `coupon_receive` | 🟡 中等 | mini-server, promotion-service, member-service |
| `member_level_upgrade` | 🟡 中等 | member-service, MQ |
| `order_create` | 🔴 复杂 | mini-server, order-service, product-service, promotion-service, member-service |
| `order_pay` | 🔴 复杂 | mini-server, order-service, 微信支付, member-service, promotion-service |
| `order_refund` | 🔴 复杂 | admin-server, order-service, 微信支付, product-service, promotion-service, member-service |

## 目录结构

```
fresh-mart/
├── README.md                       # 本文件
├── CLAUDE.md                       # AI 编码总入口（vibe-blocks claude-md 生成）
├── admin-server/                   # 运营后台 BFF（伪代码）
├── mini-server/                    # C 端小程序 BFF（伪代码）
├── member-service/                 # 会员服务（伪代码）
├── order-service/                  # 订单服务（伪代码）
├── product-service/                # 商品服务（伪代码）
├── promotion-service/              # 营销服务（伪代码）
└── .ai/                            # AI 知识库
    ├── OVERVIEW.md                 # 项目全貌
    ├── conventions.md              # 编码约定
    ├── blocks/                     # 8 个业务积木 + 索引
    ├── services/                   # 6 份服务档案
    ├── references/                 # 枚举速查、跨服务数据归属
    └── decisions/                  # ADR
```

## 学习建议

1. **新人路径**：先读 `.ai/OVERVIEW.md` → 浏览 `blocks-view.html` 可视化 → 挑一个简单积木（`member_register`）顺着锚点读伪代码 → 进阶看 `order_create` 复杂流程
2. **接入参考**：照着 `.ai/conventions.md` 给自己项目定规范，照着积木格式开始写
3. **AI 协作**：把 `CLAUDE.md` + 相关积木丢给 Claude / Cursor，AI 立刻能写出符合项目惯例的代码
