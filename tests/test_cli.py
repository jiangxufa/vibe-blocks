"""端到端验证四个一键命令。"""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from vibe_blocks.cli import main


def test_init_creates_skeleton(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["init", "--path", str(tmp_path), "--name", "demo"])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "CLAUDE.md").exists()
    assert (tmp_path / ".ai" / "OVERVIEW.md").exists()
    assert (tmp_path / ".ai" / "conventions.md").exists()
    assert (tmp_path / ".ai" / "blocks" / "_template.md").exists()
    assert (tmp_path / ".ai" / "blocks" / "_index.md").exists()


def test_new_creates_block_and_registers_index(tmp_path: Path) -> None:
    runner = CliRunner()
    runner.invoke(main, ["init", "--path", str(tmp_path), "--name", "demo"])

    ai_dir = str(tmp_path / ".ai")
    result = runner.invoke(
        main,
        [
            "new",
            "order_create",
            "--name",
            "创建订单",
            "--services",
            "api-gateway,order-service",
            "--triggers",
            "POST /api/orders",
            "--owner",
            "order-team",
            "--ai-dir",
            ai_dir,
            "--group",
            "订单",
        ],
    )
    assert result.exit_code == 0, result.output
    block = tmp_path / ".ai" / "blocks" / "order_create.md"
    assert block.exists()
    text = block.read_text(encoding="utf-8")
    assert "id: order_create" in text
    assert "name: 创建订单" in text
    assert "[api-gateway, order-service]" in text

    index = (tmp_path / ".ai" / "blocks" / "_index.md").read_text(encoding="utf-8")
    assert "## 订单" in index
    assert "(order_create.md)" in index


def test_build_generates_html(tmp_path: Path) -> None:
    runner = CliRunner()
    runner.invoke(main, ["init", "--path", str(tmp_path), "--name", "demo"])
    ai_dir = str(tmp_path / ".ai")
    runner.invoke(
        main,
        [
            "new",
            "order_create",
            "--name",
            "创建订单",
            "--services",
            "api-gateway,order-service",
            "--ai-dir",
            ai_dir,
        ],
    )

    out_html = tmp_path / "out.html"
    result = runner.invoke(
        main,
        [
            "build",
            "--blocks-dir",
            str(tmp_path / ".ai" / "blocks"),
            "--output",
            str(out_html),
        ],
    )
    assert result.exit_code == 0, result.output
    assert out_html.exists()
    html = out_html.read_text(encoding="utf-8")
    assert "BLOCKS_DATA" in html
    assert "order_create" in html


def test_claude_md_includes_blocks_index(tmp_path: Path) -> None:
    runner = CliRunner()
    runner.invoke(main, ["init", "--path", str(tmp_path), "--name", "demo"])
    ai_dir = str(tmp_path / ".ai")
    runner.invoke(
        main,
        [
            "new",
            "order_create",
            "--name",
            "创建订单",
            "--ai-dir",
            ai_dir,
            "--group",
            "订单",
        ],
    )

    result = runner.invoke(
        main,
        ["claude-md", "--path", str(tmp_path), "--force"],
    )
    assert result.exit_code == 0, result.output
    claude_md = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "order_create" in claude_md
    assert "创建订单" in claude_md
