# 贡献指南

感谢对 vibe-blocks 的关注！本项目欢迎以下形式的贡献：

- 🐛 报告 Bug
- 💡 提出新特性建议
- 📖 改进文档
- 🔧 提交 Pull Request
- 🌍 翻译文档（i18n）
- 📦 分享你的实战案例（`examples/`）

## 开发环境搭建

```bash
git clone https://github.com/jiangxufa/vibe-blocks
cd vibe-blocks

# 推荐使用虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码风格检查
ruff check src/ tests/
ruff format --check src/ tests/
```

## 代码规范

- Python 代码遵循 [PEP 8](https://peps.python.org/pep-0008/)，由 `ruff` 统一管理
- 命令实现放在 `src/vibe_blocks/commands/`，每个命令一个文件
- 模板资源放在 `src/vibe_blocks/templates/`，作为 package data 打包
- 新增命令需补充 `--help` 文案和 `tests/test_<cmd>.py`

## 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/v1.0.0/)：

```
feat: 新增 vibe-blocks watch 命令
fix: 修复 build 在 Windows 路径分隔符问题
docs: 完善老项目接入指南
refactor: 抽取 frontmatter 解析为独立模块
test: 补充 init 命令的集成测试
chore: 升级 click 到 8.1
```

## Pull Request 流程

1. Fork 本仓库 → 新建特性分支：`git checkout -b feat/your-feature`
2. 提交修改并补充测试
3. 确保 `pytest` 全绿，`ruff check` 无报错
4. 提 PR 到 `main` 分支，描述清楚变更目的和影响范围
5. 等待 review，按反馈调整

## 报告 Bug

提 Issue 时请包含：

- vibe-blocks 版本（`vibe-blocks --version`）
- Python 版本和操作系统
- 重现步骤（最小可复现示例最好）
- 期望行为 vs 实际行为
- 相关错误日志

## 提案新特性

新特性请先开 [Discussion](https://github.com/jiangxufa/vibe-blocks/discussions) 讨论，避免重复造轮子。讨论达成共识后再开 Issue 或直接提 PR。

## 文档贡献

文档源文件在 `docs/`，使用 Markdown 编写。建议：

- 短句优先，避免长难句
- 多用代码示例和图表
- 中文优先，逐步推进英文版（`docs/en/`）

## 案例分享

把你的项目接入 vibe-blocks 后的成果分享到 `examples/`：

```
examples/your-case/
├── README.md           # 案例说明（背景、规模、效果）
├── .ai/blocks/         # 脱敏后的积木示例（5-10 个）
└── screenshot.png      # 可视化页面截图
```

## 行为准则

参与本项目即表示你认可 [Contributor Covenant](https://www.contributor-covenant.org/zh-cn/version/2/1/code_of_conduct/) 行为准则。

## License

贡献的代码默认采用 MIT 协议。
