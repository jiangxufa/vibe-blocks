"""解析 .ai/blocks/*.md → 提取结构化数据。

复用并改造自 generate-blocks.py，作为 vibe-blocks 内置解析器。
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def parse_frontmatter(content: str) -> dict[str, Any]:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return {}
    fm: dict[str, Any] = {}
    for line in match.group(1).strip().split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            if val.startswith("[") and val.endswith("]"):
                val = [v.strip().strip("\"").strip("'") for v in val[1:-1].split(",") if v.strip()]
            fm[key] = val
    return fm


def extract_mermaid(content: str) -> str:
    match = re.search(r"```mermaid\s*\n(.*?)```", content, re.DOTALL)
    return match.group(1).strip() if match else ""


def extract_all_mermaids(content: str) -> str:
    matches = re.findall(r"```mermaid\s*\n(.*?)```", content, re.DOTALL)
    return "\n".join(m.strip() for m in matches) if matches else ""


def extract_steps(content: str) -> list[str]:
    steps: list[str] = []
    mermaid = extract_all_mermaids(content)
    if not mermaid:
        return steps

    alias_map: dict[str, str] = {}
    for line in mermaid.split("\n"):
        line = line.strip()
        m = re.match(r"participant\s+(\w+)\s+as\s+(.*)", line)
        if m:
            alias_map[m.group(1)] = m.group(2).strip()

    for line in mermaid.split("\n"):
        line = line.strip()
        m = re.match(r"(\w+)\s*-?->>-?\s*(\w+)\s*:\s*(.*)", line)
        if m:
            src_alias, dst_alias, msg = m.group(1), m.group(2), m.group(3).strip()
            src = alias_map.get(src_alias, src_alias)
            dst = alias_map.get(dst_alias, dst_alias)
            if src_alias == dst_alias:
                steps.append(f"[{src}] {msg}")
            else:
                steps.append(f"{src}→{dst}: {msg}")
    return steps


def extract_errors(content: str) -> list[list[str]]:
    errors: list[list[str]] = []
    match = re.search(
        r"## 异常路径\s*\n\s*\|.*\n\s*\|[-| ]+\|\s*\n((?:\s*\|.*\n?)*)",
        content,
    )
    if not match:
        return errors
    for line in match.group(1).strip().split("\n"):
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) >= 3 and cells[0]:
            errors.append(cells[:3])
    return errors


def extract_note(content: str) -> str:
    notes: list[str] = []
    for header in [r"## 特殊说明", r"## 与.*?的区别"]:
        match = re.search(header + r"\s*\n\s*(.*?)(?=\n##|\Z)", content, re.DOTALL)
        if match:
            for line in match.group(1).strip().split("\n"):
                line = line.strip()
                if line and not line.startswith("|") and not line.startswith("-"):
                    notes.append(re.sub(r"`([^`]*)`", r"\1", line))
                    break
    return " ".join(notes) if notes else ""


def extract_writes(content: str) -> list[str]:
    match = re.search(r"\*\*写表\*\*[：:]\s*(.*)", content)
    if not match:
        match = re.search(r"写表[：:]\s*(.*)", content)
    if match:
        raw = match.group(1)
        raw = re.sub(r"`([^`]*)`", r"\1", raw)
        raw = re.sub(r"\（.*?\）|\(.*?\)", "", raw)
        tables = [t.strip().strip("`").strip() for t in re.split(r"[,，、]", raw)]
        return [t for t in tables if t and not t.startswith("-") and t != "无"]
    return []


def extract_has_mq(content: str) -> bool:
    return "RocketMQ" in content or "Kafka" in content or "MQ:" in content or "MQ (" in content


def parse_index(index_path: Path) -> dict[str, list[str]]:
    """解析 _index.md，提取 ## 分组 下的积木 id 列表。"""
    groups: dict[str, list[str]] = {}
    current: str | None = None
    if not index_path.exists():
        return groups
    for line in index_path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^##\s+(.*)", line)
        if m:
            current = m.group(1).strip()
            groups.setdefault(current, [])
            continue
        # 支持 - [name](id.md) 或 | [name](id.md) | 两种格式
        m = re.search(r"\[[^\]]+\]\(([\w-]+)\.md\)", line)
        if m and current:
            groups[current].append(m.group(1))
    return groups


def parse_block_file(filepath: Path) -> dict[str, Any] | None:
    content = filepath.read_text(encoding="utf-8")
    fm = parse_frontmatter(content)
    if not fm.get("id"):
        return None
    return {
        "id": fm.get("id", ""),
        "name": fm.get("name", ""),
        "owner": fm.get("owner", ""),
        "status": fm.get("status", "draft"),
        "last_modified": fm.get("last_modified", ""),
        "services": fm.get("services", []),
        "trigger": fm.get("triggers", ""),
        "hasMQ": extract_has_mq(content),
        "steps": extract_steps(content),
        "mermaid": extract_mermaid(content),
        "errors": extract_errors(content),
        "note": extract_note(content),
        "writes": extract_writes(content),
    }


def parse_blocks_dir(blocks_dir: Path) -> tuple[dict[str, list[dict]], dict[str, int]]:
    """解析整个 blocks/ 目录，返回 (按分组组织的数据, 统计)。"""
    if not blocks_dir.exists():
        raise FileNotFoundError(f"未找到目录：{blocks_dir}")

    index_groups = parse_index(blocks_dir / "_index.md")

    all_blocks: dict[str, dict[str, Any]] = {}
    for f in sorted(blocks_dir.glob("*.md")):
        if f.name.startswith("_"):
            continue
        block = parse_block_file(f)
        if block:
            all_blocks[block["id"]] = block

    output: dict[str, list[dict]] = {}
    assigned: set[str] = set()
    for group_name, block_ids in index_groups.items():
        group_blocks = []
        for bid in block_ids:
            if bid in all_blocks and bid not in assigned:
                group_blocks.append(all_blocks[bid])
                assigned.add(bid)
        if group_blocks:
            output[group_name] = group_blocks

    ungrouped = [b for bid, b in all_blocks.items() if bid not in assigned]
    if ungrouped:
        output["未分组"] = ungrouped

    stats = {
        "total": len(all_blocks),
        "stable": sum(1 for b in all_blocks.values() if b["status"] == "stable"),
        "draft": sum(1 for b in all_blocks.values() if b["status"] == "draft"),
        "deprecated": sum(1 for b in all_blocks.values() if b["status"] == "deprecated"),
    }
    return output, stats


def render_data_js(output: dict, stats: dict) -> str:
    return (
        "// vibe-blocks build 自动生成，请勿手动编辑\n"
        f"// 积木数量: {stats['total']} | 分组: {len(output)}\n\n"
        f"const BLOCKS_DATA = {json.dumps(output, ensure_ascii=False, indent=2)};\n\n"
        f"const BLOCKS_STATS = {json.dumps(stats, ensure_ascii=False, indent=2)};\n"
    )
