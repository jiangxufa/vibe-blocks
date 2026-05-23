# 积木可视化网页生成

将 `.ai/blocks/` 目录下的积木文件自动解析为交互式架构图网页，方便团队浏览和分享。

## 文件说明

```
05-visualization/
├── README.md                  # 本文档
├── generate-blocks.py         # 解析脚本：.md → .js 数据
├── project-blocks.html        # 网页模板（引用外部数据）
├── build.sh                   # 一键生成脚本
└── example-output.html        # 示例输出（fresh-mart，8 个积木）
```

## 快速使用

### 方式一：一键生成（推荐）

```bash
# 在项目根目录执行
bash /path/to/sop/jimu/05-visualization/build.sh .ai/blocks ./docs/blocks-view.html
```

参数说明：
- 参数1：积木目录路径（默认 `.ai/blocks`）
- 参数2：输出文件路径（默认 `./project-blocks-standalone.html`）

### 方式二：分步执行

```bash
# 第1步：解析积木 → 生成数据文件
python3 generate-blocks.py .ai/blocks project-blocks-data.js

# 第2步：合并数据到 HTML → 生成独立网页
python3 -c "
with open('project-blocks.html') as f:
    html = f.read()
with open('project-blocks-data.js') as f:
    data = f.read()
html = html.replace('<script src=\"./project-blocks-data.js\"></script>', f'<script>\n{data}\n</script>')
with open('project-blocks-standalone.html', 'w') as f:
    f.write(html)
"
```

## 输出产物

| 文件 | 用途 | 说明 |
|------|------|------|
| `project-blocks-data.js` | 中间数据 | JSON 格式的积木数据，可被其他工具消费 |
| `project-blocks-standalone.html` | 最终产物 | 独立 HTML 文件，仅依赖 mermaid CDN，可直接分享 |

## 网页功能

- **架构图拓扑**：按 BFF → 核心服务 → 基础设施分层展示
- **服务节点点击**：点击服务查看其支持的所有功能积木
- **积木详情**：展开查看调用链路、时序图、异常路径、备注
- **时序图渲染**：Mermaid 实时渲染序列图
- **分组聚合**：积木按业务域分组展示

## 自定义架构拓扑

vibe-blocks 会**自动**从积木里推导出服务拓扑，按命名规则归类成 BFF / 核心业务 / 基础设施 / 外部系统四层 — 通常你不需要任何额外配置。

推导规则：

- `xxx-server` / `xxx-bff` / `xxx-gateway` / `xxx-portal` → BFF 层
- `MySQL` / `Redis` / `MQ` / `Kafka` / `OSS` / `数据库` 等 → 基础设施层（展示时抽象为「数据库」「消息队列」「对象存储」等通用名）
- `Alipay` / `微信` / `Stripe` / `第三方` 等 → 外部系统层（抽象为「支付平台」「短信网关」等）
- 其余 → 核心业务层

如需自定义标题或副标题，使用 CLI 参数：

```bash
vibe-blocks build \
    --title "My Project" \
    --subtitle "点击节点查看积木详情"
```

如果默认推导规则不满足需要（比如想固定 layer 顺序、加自定义 layer），有两种方式：

1. **后处理 HTML**：用 `vibe-blocks build --data-only` 只生成数据 JS，自己写 HTML 模板引用
2. **在 OVERVIEW.md 中标注**：未来版本会支持从 `.ai/OVERVIEW.md` 显式声明 layers（roadmap）

**规则**：

- `services` 数组中的名称应与积木 frontmatter 的 `services` 字段一致
- `type` 决定节点颜色：`bff`=蓝色, `core`=紫色, `infra`=绿色, `external`=橙色
- 同一 `type` 的多个 layer 之间不显示箭头

## 常见问题

### Q: 某些积木没有出现在网页上？
A: 检查积木的 `services` 字段是否包含 `layers` 中定义的服务名。如果积木引用了未在拓扑中定义的服务，该积木只能通过其他已定义的服务入口访问。

### Q: 如何更新网页？
A: 积木文件变更后，重新执行 `build.sh` 即可。建议在 CI/CD 中集成自动生成。

### Q: 网页打不开时序图？
A: 需要网络连接加载 mermaid CDN（`cdnjs.cloudflare.com`）。离线环境需要将 mermaid.js 下载到本地并修改引用路径。
