# vibe-blocks 文档

> 业务流程积木化文档体系的完整使用手册。

## 快速导航

### 我是新人，想快速了解
- [核心概念](01-quickstart/01-concept.md)
- [5 分钟快速上手](01-quickstart/02-quick-start.md)

### 我要启动新项目
- [新项目初始化](02-initialization/01-new-project.md)（推荐用 `vibe-blocks init`）

### 我要给老项目引入积木体系
- [老项目接入](02-initialization/02-existing-project.md)

### 我要创建/更新/使用积木
- [创建积木](03-operations/01-create-block.md)（推荐用 `vibe-blocks new`）
- [更新积木](03-operations/02-update-block.md)
- [使用积木](03-operations/03-use-block.md)

### 我们团队要协作维护积木
- [团队协作流程](04-collaboration/01-team-workflow.md)
- [冲突解决](04-collaboration/02-merge-conflicts.md)

### 我要生成可视化网页
- [可视化工具](05-visualization/README.md)（推荐用 `vibe-blocks build`）

## CLI 命令速查

| 命令 | 用途 | 替代手工操作 |
|------|------|------|
| `vibe-blocks init` | 一键初始化项目 | 手动 `mkdir .ai/{blocks,services,...}` 并创建模板 |
| `vibe-blocks new <id>` | 一键创建新积木 | 手动 `cp _template.md xxx.md` 并改 `_index.md` |
| `vibe-blocks build` | 一键生成可视化 HTML | 手动跑 `python generate-blocks.py` + `build.sh` |
| `vibe-blocks claude-md` | 一键扫描项目刷新 `CLAUDE.md` | 手动维护技术栈和积木索引 |

每个命令都支持 `--help` 查看完整参数。

## 核心原则

1. **代码即文档**：积木与代码同 PR 提交，强制同步
2. **锚点驱动**：每个节点逻辑都有真实代码锚点，确保可追溯
3. **最小粒度**：一个积木 = 一条完整业务流程
4. **持续演进**：积木记录变更历史，追踪流程演进

## 常见问题

### Q: 积木文件放在哪里？
A: 默认 `.ai/blocks/`，由 `vibe-blocks init` 自动创建。

### Q: 什么时候需要更新积木？
A: 修改业务流程相关代码时（新增/删除服务调用、修改处理步骤、改变异常处理）。

### Q: 我的项目不是 Java 怎么办？
A: 积木体系与语言无关，只需调整锚点格式。Go: `pkg/service/user.go#CreateUser`，Python: `service/user.py#create_user`，Node.js: `src/services/user.service.ts#createUser`。

### Q: 多人同时改同一个积木怎么办？
A: 参考 [冲突解决](04-collaboration/02-merge-conflicts.md)。

## 贡献指南

欢迎完善文档：

1. 发现错误或不清晰的地方，提 Issue
2. 有更好的实践经验，提 PR 补充
3. 新增工具或流程，更新对应章节
