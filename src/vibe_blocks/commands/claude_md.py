"""vibe-blocks claude-md — 一键扫描项目，生成/刷新 CLAUDE.md。"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import click

from vibe_blocks.parsers import parse_blocks_dir
from vibe_blocks.utils import template_text

# 用文件存在性识别技术栈
TECH_STACK_DETECTORS = [
    ("Java + Maven", ["pom.xml"]),
    ("Java + Gradle", ["build.gradle", "build.gradle.kts"]),
    ("Node.js + npm", ["package.json"]),
    ("Python + Poetry", ["pyproject.toml"]),
    ("Python + pip", ["requirements.txt", "setup.py"]),
    ("Go Modules", ["go.mod"]),
    ("Rust + Cargo", ["Cargo.toml"]),
    ("Ruby + Bundler", ["Gemfile"]),
    ("PHP + Composer", ["composer.json"]),
    ("Spring Boot", ["application.yml", "application.properties"]),
    ("Docker", ["Dockerfile", "docker-compose.yml"]),
    ("Kubernetes", ["k8s/", "kubernetes/"]),
]


def detect_tech_stack(root: Path) -> list[str]:
    found: list[str] = []
    for label, markers in TECH_STACK_DETECTORS:
        for marker in markers:
            if marker.endswith("/"):
                if (root / marker.rstrip("/")).is_dir():
                    found.append(label)
                    break
            else:
                # 仅检查根目录或一级子目录
                if (root / marker).exists():
                    found.append(label)
                    break
                if any(p.exists() for p in root.glob(f"*/{marker}")):
                    found.append(label)
                    break
    # 去重保序
    seen: set[str] = set()
    result: list[str] = []
    for x in found:
        if x not in seen:
            seen.add(x)
            result.append(x)
    return result


def render_blocks_index(blocks_dir: Path) -> str:
    """生成嵌入 CLAUDE.md 的积木索引片段。"""
    if not blocks_dir.exists():
        return "_暂无积木，运行 `vibe-blocks new <id>` 创建第一个。_"

    output_data, stats = parse_blocks_dir(blocks_dir)
    if stats["total"] == 0:
        return "_暂无积木，运行 `vibe-blocks new <id>` 创建第一个。_"

    lines = [
        f"积木总数：**{stats['total']}**（stable={stats['stable']}, "
        f"draft={stats['draft']}, deprecated={stats.get('deprecated', 0)}）",
        "",
    ]
    for group, blocks in output_data.items():
        lines.append(f"### {group}")
        lines.append("")
        for b in blocks:
            status_badge = {
                "stable": "✅",
                "draft": "🟡",
                "deprecated": "⚠️",
            }.get(b["status"], "·")
            lines.append(
                f"- {status_badge} [`{b['id']}`](.ai/blocks/{b['id']}.md) "
                f"— {b['name']}"
                + (f"（{b['trigger']}）" if b.get("trigger") else "")
            )
        lines.append("")
    return "\n".join(lines).rstrip()


@click.command(help="一键扫描项目结构与积木索引，构建/刷新根目录 CLAUDE.md。")
@click.option(
    "--path",
    "project_path",
    default=".",
    show_default=True,
    type=click.Path(file_okay=False, resolve_path=True),
    help="项目根目录。",
)
@click.option(
    "--ai-dir",
    default=".ai",
    show_default=True,
    help=".ai 目录路径（相对项目根）。",
)
@click.option(
    "--output",
    default="CLAUDE.md",
    show_default=True,
    help="输出文件名。",
)
@click.option("--force", is_flag=True, help="覆盖已有 CLAUDE.md（默认会创建备份）。")
def claude_md_cmd(
    project_path: str, ai_dir: str, output: str, force: bool
) -> None:
    root = Path(project_path)
    if not root.exists():
        raise click.ClickException(f"项目目录不存在：{root}")

    name = root.name
    blocks_dir = root / ai_dir / "blocks"

    tech_stack = detect_tech_stack(root)
    tech_stack_md = (
        "\n".join(f"- {t}" for t in tech_stack) if tech_stack else "_未检测到，请手动补充_"
    )

    blocks_index = render_blocks_index(blocks_dir)

    tmpl = template_text("CLAUDE.md.tmpl")
    rendered = (
        tmpl.replace("{{PROJECT_NAME}}", name)
        .replace("{{DATE}}", date.today().isoformat())
        .replace("{{TECH_STACK}}", tech_stack_md)
        .replace("{{BLOCKS_INDEX}}", blocks_index)
    )

    out = root / output
    if out.exists() and not force:
        backup = out.with_suffix(out.suffix + ".bak")
        out.rename(backup)
        click.echo(click.style(f"  · 已备份原文件：{backup.name}", fg="yellow"))

    out.write_text(rendered, encoding="utf-8")
    click.echo(click.style(f"✓ 已生成：{out}", fg="green", bold=True))
    click.echo(f"  技术栈：{', '.join(tech_stack) if tech_stack else '未检测到'}")
    click.echo("  积木索引已嵌入。")
