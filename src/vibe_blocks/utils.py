"""模板与资源加载工具。"""

from __future__ import annotations

import sys
from importlib import resources
from pathlib import Path


def template_text(name: str) -> str:
    """读取打包内的模板文件文本（位于 vibe_blocks/templates/）。"""
    pkg = "vibe_blocks.templates"
    if sys.version_info >= (3, 9):
        return resources.files(pkg).joinpath(name).read_text(encoding="utf-8")
    # Python 3.8 fallback
    with resources.open_text(pkg, name, encoding="utf-8") as f:  # type: ignore[arg-type]
        return f.read()


def asset_text(name: str) -> str:
    """读取打包内的静态资源（位于 vibe_blocks/assets/）。"""
    pkg = "vibe_blocks.assets"
    if sys.version_info >= (3, 9):
        return resources.files(pkg).joinpath(name).read_text(encoding="utf-8")
    with resources.open_text(pkg, name, encoding="utf-8") as f:  # type: ignore[arg-type]
        return f.read()


def write_if_absent(path: Path, content: str, *, force: bool = False) -> bool:
    """写入文件；存在且未启用 force 时跳过。返回是否写入。"""
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True
