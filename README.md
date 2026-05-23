<div align="center">

# vibe-blocks

**让 AI 真正读懂你的代码 — 业务流程积木化文档体系**

[![PyPI version](https://img.shields.io/pypi/v/vibeblocks-cli.svg)](https://pypi.org/project/vibeblocks-cli/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-online-blueviolet.svg)](docs/)

[快速开始](#-quick-start) ·
[核心理念](#-为什么需要-vibe-blocks) ·
[文档](docs/) ·
[示例](examples/) ·
[贡献](CONTRIBUTING.md)

</div>

---

## ✨ 是什么

**vibe-blocks** 是一套面向 AI 辅助开发（vibe coding）的业务流程文档化方法和配套工具。

它把每条完整业务流程拆解成一个**积木**（Markdown 文件，含 YAML 元信息 + Mermaid 时序图 + 节点逻辑 + 异常路径 + 变更记录），让 Claude / Cursor / Copilot 等 AI 助手在编码时拥有真正的业务上下文，而不是反复猜读源码。

```
代码 ←→ 积木 ←→ AI
   维护同步     精准上下文
```

## 🚀 Quick Start

```bash
# 安装
pip install vibeblocks-cli

# 在你的项目根目录一键初始化
cd your-project
vibe-blocks init

# 一键创建新积木
vibe-blocks new order_create --name "创建订单" --services api-gateway,order-service

# 一键生成可视化 HTML
vibe-blocks build

# 一键扫描代码刷新 CLAUDE.md
vibe-blocks claude-md
```

打开生成的 `project-blocks.html`，你会看到所有业务流程的**交互式架构图** —— 点击任一服务，展开它支撑的所有功能积木。

## 🎯 为什么需要 vibe-blocks

### 微服务时代，AI 编码的 4 大痛点

| 痛点 | 现状 | vibe-blocks 怎么解 |
|------|------|------|
| **新人上手难** | 一个功能跨多个服务，调用链不清晰 | 积木一图看尽完整链路 |
| **代码维护难** | 改了代码不知影响哪些流程 | 锚点反向定位，强制同步更新 |
| **问题排查难** | 不知从哪个服务开始查 | 时序图 + 异常路径直接命中 |
| **AI 编码偏差** | AI 反复猜读源码，输出不准 | 积木提供精准业务上下文 |

### 一个积木长什么样

```markdown
---
id: order_create
name: 创建订单
services: [api-gateway, order-service, inventory-service]
triggers: POST /api/v1/orders
status: stable
---

## 流程总览
\`\`\`mermaid
sequenceDiagram
    participant C as 客户端
    participant G as api-gateway
    participant O as order-service
    participant I as inventory-service

    C->>G: POST /api/v1/orders
    G->>O: gRPC: CreateOrder
    O->>I: 扣减库存
    O-->>G: order_id
    G-->>C: 200
\`\`\`

## 节点逻辑
### order-service — 核心业务
**入口**：`OrderController#createOrder`
**锚点**：`order-service/src/.../OrderController.java#createOrder`

处理步骤：
1. 参数校验
2. 调用库存扣减
3. 持久化订单
...

## 异常路径
| 场景 | 处理 | 返回 |
|------|------|------|
| 库存不足 | 抛 InsufficientStockException | "库存不足" |

## 变更记录
- 2026-05-23: 新增库存预扣机制（MR-1234）
```

## 📦 核心命令

| 命令 | 用途 |
|------|------|
| `vibe-blocks init` | 一键初始化项目（创建 `.ai/` 目录、`CLAUDE.md`、模板文件） |
| `vibe-blocks new <id>` | 一键创建新积木，自动注册到 `_index.md` |
| `vibe-blocks build` | 一键生成可视化 HTML 网页（含架构图 + 时序图 + 异常路径） |
| `vibe-blocks claude-md` | 一键扫描项目 + 积木索引，构建/刷新 `CLAUDE.md` |

每个命令都有 `--help`，详细参数见 [docs/](docs/)。

## 🏗 工作流

```
                  ┌────────────────────────────┐
                  │  vibe-blocks init          │
                  │  生成 .ai/ + CLAUDE.md     │
                  └────────────┬───────────────┘
                               ↓
        ┌──────────────────────┴──────────────────────┐
        │                                             │
   日常开发                                       Code Review
        │                                             │
   ┌────▼────┐  改代码 ┌────────┐  自动校验   ┌────▼────┐
   │ 写代码  │ ───→   │更新积木 │ ───────→   │ lint  │
   └─────────┘        └────────┘             └─────────┘
        │                  │                       │
        └────────┬─────────┴───────────────────────┘
                 ↓
        ┌────────────────────────┐
        │ vibe-blocks build      │
        │ 生成可视化 HTML 分享   │
        └────────────────────────┘
```

## 🌟 核心特性

- **零运行时依赖**：积木就是 Markdown，无需任何运行时
- **AI 原生**：与 Claude / Cursor 等 AI 助手深度集成
- **代码即文档**：积木与代码同 PR 提交，强制同步
- **可视化即时**：一键生成交互式架构图网页
- **语言无关**：Java / Go / Python / Node.js 都能用，只是锚点格式不同
- **粒度合理**：一个积木 = 一条完整业务流程（不细到参数校验，不粗到"订单系统"）

## 📚 文档

- [核心概念](docs/01-quickstart/01-concept.md)
- [5 分钟快速上手](docs/01-quickstart/02-quick-start.md)
- [新项目初始化](docs/02-initialization/01-new-project.md)
- [老项目接入](docs/02-initialization/02-existing-project.md)
- [创建积木](docs/03-operations/01-create-block.md)
- [更新积木](docs/03-operations/02-update-block.md)
- [使用积木](docs/03-operations/03-use-block.md)
- [团队协作](docs/04-collaboration/01-team-workflow.md)
- [冲突解决](docs/04-collaboration/02-merge-conflicts.md)
- [可视化工具](docs/05-visualization/README.md)

## 🎬 实战案例

- **`examples/fresh-mart`**：6 服务的生鲜电商示例，8 个积木（含 3 个跨 5 服务的复杂流程：下单 / 支付 / 退款），完整演示 try-compensate 模式
- 你的案例？欢迎 PR 到 `examples/`

## 🤝 参与贡献

PR / Issue / Discussion 都欢迎。详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

```bash
git clone https://github.com/jiangxufa/vibe-blocks
cd vibe-blocks
pip install -e ".[dev]"
pytest
```

## 📄 License

[MIT](LICENSE) © vibe-blocks contributors
