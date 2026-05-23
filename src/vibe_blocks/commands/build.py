"""vibe-blocks build — 一键生成可视化 HTML。"""

from __future__ import annotations

import json
import re
from pathlib import Path

import click

from vibe_blocks.parsers import parse_blocks_dir, render_data_js
from vibe_blocks.topology import (
    abstract_display_name,
    classify_service,
    collect_extras_from_mermaid,
    collect_services_from_blocks,
    derive_layers,
)
from vibe_blocks.utils import asset_text


def _read_overview_title(overview_path: Path) -> str | None:
    """从 .ai/OVERVIEW.md 顶部一级标题提取项目名（剥掉「项目全貌」之类后缀）。"""
    if not overview_path.exists():
        return None
    for line in overview_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        m = re.match(r"^#\s+(.+?)\s*$", line)
        if m:
            title = m.group(1).strip()
            # 去掉常见后缀
            for suffix in ["项目全貌", "概述", "Overview", "全貌"]:
                if title.endswith(suffix):
                    title = title[: -len(suffix)].strip()
            return title or None
    return None


def _enrich_display_services(output_data: dict) -> None:
    """就地修改 output_data：把每个积木的 services 字段补上其 mermaid 里出现的
    基础设施/外部系统的抽象名（数据库/消息队列/支付平台 等）。

    这样点击拓扑里的「数据库」节点时，能找到所有用到任意 DB 类基础设施的积木。
    """
    pat = re.compile(r"\s*participant\s+\w+\s+as\s+(.+)")
    from vibe_blocks.topology import TRIGGER_NAMES

    for blocks in output_data.values():
        for b in blocks:
            mermaid = b.get("mermaid", "") or ""
            services = list(b.get("services", []) or [])
            seen = set(services)

            for line in mermaid.split("\n"):
                m = pat.match(line.strip())
                if not m:
                    continue
                name = m.group(1).strip().strip("`")
                if not name or name in TRIGGER_NAMES or name in seen:
                    continue
                kind = classify_service(name)
                if kind in ("infra", "external"):
                    alias = abstract_display_name(name, kind)
                    if alias not in seen:
                        seen.add(alias)
                        services.append(alias)
            b["services"] = services


@click.command(help="一键解析 .ai/blocks/ 并生成独立 HTML 网页（含交互式架构图）。")
@click.option(
    "--blocks-dir",
    default=".ai/blocks",
    show_default=True,
    type=click.Path(file_okay=False),
    help="积木目录路径。",
)
@click.option(
    "--output",
    default="./project-blocks.html",
    show_default=True,
    type=click.Path(dir_okay=False),
    help="输出 HTML 文件路径。",
)
@click.option(
    "--title",
    default=None,
    help="项目标题（默认从 .ai/OVERVIEW.md 顶部标题或目录名推导）。",
)
@click.option(
    "--subtitle",
    default="点击服务节点查看其支持的功能积木",
    show_default=True,
    help="副标题。",
)
@click.option(
    "--data-only",
    is_flag=True,
    help="仅输出数据 JS 文件（搭配自定义 HTML 模板使用）。",
)
def build_cmd(
    blocks_dir: str,
    output: str,
    title: str | None,
    subtitle: str,
    data_only: bool,
) -> None:
    blocks_path = Path(blocks_dir)
    output_path = Path(output)

    output_data, stats = parse_blocks_dir(blocks_path)

    # 自动推导服务拓扑（基于积木里出现过的所有服务名 + mermaid 中的基础设施/外部系统）
    services = collect_services_from_blocks(output_data)
    extras = collect_extras_from_mermaid(output_data, set(services))
    layers = derive_layers(services + extras)

    # 回填每个积木的 services 字段：把 mermaid 里出现的具体技术名（PolarDB/RocketMQ/微信支付）
    # 替换为抽象层名（数据库/消息队列/支付平台），让点击节点能定位到对应积木。
    _enrich_display_services(output_data)
    data_js = render_data_js(output_data, stats)
    layers_js = (
        f"const LAYERS_DATA = {json.dumps(layers, ensure_ascii=False, indent=2)};"
    )

    # 推导项目标题
    if title is None:
        # 1) 优先从 .ai/OVERVIEW.md 抓
        overview = blocks_path.parent / "OVERVIEW.md"
        title = _read_overview_title(overview)
    if title is None:
        # 2) 退到项目根目录名
        title = blocks_path.parent.parent.resolve().name

    if data_only:
        out = output_path.with_suffix(".js")
        out.parent.mkdir(parents=True, exist_ok=True)
        # 仅数据模式也带上 layers 与元信息，方便复用
        out.write_text(
            f"const PROJECT_TITLE = {json.dumps(title, ensure_ascii=False)};\n"
            f"const PROJECT_SUBTITLE = {json.dumps(subtitle, ensure_ascii=False)};\n\n"
            f"{data_js}\n{layers_js}\n",
            encoding="utf-8",
        )
        click.echo(click.style(f"✓ 已生成数据文件：{out}", fg="green", bold=True))
    else:
        html_tmpl = asset_text("project-blocks.html")
        marker = '<script src="./project-blocks-data.js"></script>'
        if marker not in html_tmpl:
            raise click.ClickException("HTML 模板格式异常，找不到数据占位脚本。")

        # 拼接所有 inline 数据
        inline = (
            f"<script>\n{data_js}\n{layers_js}\n</script>"
        )
        html_out = (
            html_tmpl
            .replace(marker, inline)
            .replace("{{PROJECT_TITLE}}", title)
            .replace("{{PROJECT_SUBTITLE}}", subtitle)
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_out, encoding="utf-8")
        click.echo(
            click.style(f"✓ 已生成可视化：{output_path}", fg="green", bold=True)
        )

    click.echo(f"  项目标题：{title}")
    click.echo(
        f"  积木总数：{stats['total']} "
        f"(stable={stats['stable']}, draft={stats['draft']}, "
        f"deprecated={stats.get('deprecated', 0)})"
    )
    click.echo(f"  分组数量：{len(output_data)}")
    click.echo(
        f"  服务拓扑：BFF={sum(1 for lyr in layers if lyr['type']=='bff')}层, "
        f"core={sum(len(lyr['services']) for lyr in layers if lyr['type']=='core')}, "
        f"infra={sum(len(lyr['services']) for lyr in layers if lyr['type']=='infra')}, "
        f"external={sum(len(lyr['services']) for lyr in layers if lyr['type']=='external')}"
    )
