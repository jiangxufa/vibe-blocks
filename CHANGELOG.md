# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-05-23

### Fixed
- 修复 ruff E741 报错（重命名 build.py 中的变量 l → lyr）

## [0.1.0] - 2026-05-23

### Added
- 初版发布
- `vibe-blocks init`：一键初始化项目（创建 `.ai/` 目录、`CLAUDE.md`、`conventions.md`、`OVERVIEW.md`、`_template.md`、`_index.md`）
- `vibe-blocks new <id>`：一键创建新积木，自动注册到索引
- `vibe-blocks build`：一键解析积木并生成独立 HTML 可视化网页（含架构图 + Mermaid 时序图）
- `vibe-blocks claude-md`：一键扫描项目结构 + 积木索引，构建/刷新 `CLAUDE.md`
- 完整 SOP 文档（5 章节，覆盖快速上手、初始化、日常运维、团队协作、可视化）
- 支持 Java / Go / Python / Node.js 多语言锚点格式

[Unreleased]: https://github.com/jiangxufa/vibe-blocks/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/jiangxufa/vibe-blocks/releases/tag/v0.1.0
