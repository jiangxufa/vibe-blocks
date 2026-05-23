"""vibe-blocks new <id> — 一键创建新积木并注册到索引。"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import click

from vibe_blocks.utils import template_text


def _slug_ok(name: str) -> bool:
    return bool(re.fullmatch(r"[a-z][a-z0-9_]*", name))


@click.command(help="一键创建新积木文件，自动注册到 _index.md。")
@click.argument("block_id")
@click.option("--name", "block_name", default=None, help="积木中文名（默认与 id 同）。")
@click.option(
    "--services",
    default="",
    help='参与服务，逗号分隔。如 "api-gateway,order-service"。',
)
@click.option(
    "--triggers",
    default="POST /api/...",
    show_default=True,
    help="触发方式（HTTP / Cron / MQ）。",
)
@click.option("--owner", default="team", show_default=True, help="负责团队。")
@click.option(
    "--ai-dir",
    default=".ai",
    show_default=True,
    type=click.Path(file_okay=False),
    help=".ai 目录路径。",
)
@click.option(
    "--group",
    default=None,
    help="索引分组（默认归到「未分组」），可选。",
)
@click.option("--force", is_flag=True, help="覆盖已存在的积木文件。")
def new_cmd(
    block_id: str,
    block_name: str | None,
    services: str,
    triggers: str,
    owner: str,
    ai_dir: str,
    group: str | None,
    force: bool,
) -> None:
    if not _slug_ok(block_id):
        raise click.BadParameter(
            "积木 id 必须是小写字母数字下划线，且以字母开头（如 order_create）",
            param_hint="BLOCK_ID",
        )

    ai_path = Path(ai_dir)
    blocks_path = ai_path / "blocks"
    if not blocks_path.exists():
        raise click.ClickException(
            f"未找到 {blocks_path}，请先运行 `vibe-blocks init` 或确认 --ai-dir 参数。"
        )

    block_file = blocks_path / f"{block_id}.md"
    if block_file.exists() and not force:
        raise click.ClickException(
            f"积木已存在：{block_file}，使用 --force 覆盖。"
        )

    # 1) 渲染积木内容
    services_list = [s.strip() for s in services.split(",") if s.strip()]
    services_yaml = "[" + ", ".join(services_list) + "]" if services_list else "[]"

    tmpl = template_text("new-block.md.tmpl")
    content = (
        tmpl.replace("{{ID}}", block_id)
        .replace("{{NAME}}", block_name or block_id)
        .replace("{{OWNER}}", owner)
        .replace("{{DATE}}", date.today().isoformat())
        .replace("{{SERVICES}}", services_yaml)
        .replace("{{TRIGGERS}}", triggers)
    )

    block_file.write_text(content, encoding="utf-8")
    click.echo(click.style(f"✓ 创建积木：{block_file}", fg="green", bold=True))

    # 2) 注册到 _index.md
    index_file = blocks_path / "_index.md"
    if index_file.exists():
        _register_to_index(index_file, block_id, block_name or block_id, group)
        click.echo(f"  · 已注册到 {index_file}")
    else:
        click.echo(
            click.style(
                f"  ! 未找到 {index_file}，请手动添加索引或运行 `vibe-blocks init`",
                fg="yellow",
            )
        )

    click.echo()
    click.echo("下一步：")
    click.echo(f"  1. 编辑 {block_file} 填写流程图与节点逻辑")
    click.echo("  2. 运行 `vibe-blocks build` 重新生成可视化")


def _register_to_index(
    index_file: Path,
    block_id: str,
    block_name: str,
    group: str | None,
) -> None:
    """在 _index.md 中追加一行 - [中文名](id.md) — 简短描述。"""
    target_group = group or "未分组"
    line = f"- [{block_name}]({block_id}.md) — {block_name}"

    text = index_file.read_text(encoding="utf-8")

    # 已存在的引用，不重复添加
    if f"]({block_id}.md)" in text:
        return

    lines = text.splitlines()
    section_re = re.compile(r"^##\s+(.+?)\s*$")
    found_group = -1
    for i, raw in enumerate(lines):
        m = section_re.match(raw)
        if m and m.group(1).strip() == target_group:
            found_group = i
            break

    if found_group == -1:
        # 没找到分组，在文件末尾追加
        if lines and lines[-1].strip():
            lines.append("")
        lines.append(f"## {target_group}")
        lines.append("")
        lines.append(line)
        lines.append("")
    else:
        # 在该分组的最后一条目下方插入
        insert_at = len(lines)
        for j in range(found_group + 1, len(lines)):
            if section_re.match(lines[j]):
                insert_at = j
                break
        # 回退到分组内最后一个非空行后
        k = insert_at - 1
        while k > found_group and not lines[k].strip():
            k -= 1
        lines.insert(k + 1, line)

    index_file.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
