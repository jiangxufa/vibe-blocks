"""vibe-blocks init — 一键初始化项目（创建 .ai/ 目录及配套文件）。"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import click

from vibe_blocks.utils import template_text, write_if_absent

# 需要创建的子目录
SUBDIRS = ["blocks", "services", "references", "decisions", "prompts", "changelog"]


@click.command(help="一键初始化项目，创建 .ai/ 目录与 CLAUDE.md。")
@click.option(
    "--path",
    "project_path",
    default=".",
    show_default=True,
    type=click.Path(file_okay=False, resolve_path=True),
    help="项目根目录。",
)
@click.option(
    "--name",
    "project_name",
    default=None,
    help="项目名称（用于填充模板，默认取目录名）。",
)
@click.option("--force", is_flag=True, help="覆盖已存在的文件。")
def init_cmd(project_path: str, project_name: str | None, force: bool) -> None:
    root = Path(project_path)
    root.mkdir(parents=True, exist_ok=True)
    name = project_name or root.name

    ai_dir = root / ".ai"
    blocks_dir = ai_dir / "blocks"

    # 1) 创建子目录骨架
    for sub in SUBDIRS:
        (ai_dir / sub).mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    written: list[Path] = []
    skipped: list[Path] = []

    # 2) 写入模板文件
    files = {
        root / "CLAUDE.md": template_text("CLAUDE.md.tmpl").replace(
            "{{PROJECT_NAME}}", name
        ).replace("{{DATE}}", today),
        ai_dir / "OVERVIEW.md": template_text("OVERVIEW.md.tmpl").replace(
            "{{PROJECT_NAME}}", name
        ),
        ai_dir / "conventions.md": template_text("conventions.md.tmpl"),
        ai_dir / "README.md": template_text("ai-README.md.tmpl").replace(
            "{{PROJECT_NAME}}", name
        ),
        blocks_dir / "_template.md": template_text("block-template.md.tmpl"),
        blocks_dir / "_index.md": template_text("blocks-index.md.tmpl"),
    }

    for path, content in files.items():
        if write_if_absent(path, content, force=force):
            written.append(path)
        else:
            skipped.append(path)

    # 3) 输出汇总
    click.echo(click.style(f"✓ 已初始化 {name}", fg="green", bold=True))
    click.echo(f"  根目录：{root}")
    click.echo(f"  .ai/ 子目录：{', '.join(SUBDIRS)}")
    click.echo()

    if written:
        click.echo(click.style("已创建：", fg="green"))
        for p in written:
            click.echo(f"  + {p.relative_to(root)}")

    if skipped:
        click.echo(click.style("已跳过（文件已存在，--force 可覆盖）：", fg="yellow"))
        for p in skipped:
            click.echo(f"  · {p.relative_to(root)}")

    click.echo()
    click.echo("下一步：")
    click.echo("  1. 编辑 .ai/OVERVIEW.md 填写项目全貌")
    click.echo("  2. 运行 `vibe-blocks new <id>` 创建第一个积木")
    click.echo("  3. 运行 `vibe-blocks build` 生成可视化网页")
