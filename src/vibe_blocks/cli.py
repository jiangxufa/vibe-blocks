"""命令行入口：vibe-blocks <command>。"""

from __future__ import annotations

import click

from vibe_blocks import __version__
from vibe_blocks.commands import build_cmd, claude_md_cmd, init_cmd, new_cmd


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    help="vibe-blocks — 让 AI 真正读懂你的代码。",
)
@click.version_option(__version__, "-V", "--version", prog_name="vibe-blocks")
def main() -> None:
    """vibe-blocks 命令行入口。"""


main.add_command(init_cmd, name="init")
main.add_command(new_cmd, name="new")
main.add_command(build_cmd, name="build")
main.add_command(claude_md_cmd, name="claude-md")


if __name__ == "__main__":
    main()
