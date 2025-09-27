import os
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Annotated

import typer

from ultrapyup.editor import EditorRule, EditorSetting
from ultrapyup.initialize import initialize
from ultrapyup.package_manager.pm import PackageManager
from ultrapyup.precommit import PreCommitTool
from ultrapyup.utils import log


app = typer.Typer(
    name="Ultrapyup",
    help="Ship code faster and with more confidence.",
    no_args_is_help=True,
)


@contextmanager
def change_directory(path: Path) -> Generator[Path, None, None]:
    """Context manager to temporarily change directory."""
    original_cwd = Path.cwd()
    try:
        os.chdir(path)
        yield path
    finally:
        os.chdir(original_cwd)


@app.command("init", help="Initialize Ultrapyup in the current directory")
def init_command(
    path: Annotated[Path, typer.Argument(help="Directory to initialize (defaults to current directory)")] = Path("."),
    package_manager: Annotated[
        PackageManager | None,
        typer.Option(
            "--package-manager",
            "-pm",
            help="Package manager to use (uv, poetry, pip)",
        ),
    ] = None,
    editor_rules: Annotated[
        list[EditorRule] | None,
        typer.Option(
            "--editor-rules",
            "-er",
            help="AI rules to enable (github-copilot, cursor-ai, windsurf-ai, claude-md, zed-ai)",
        ),
    ] = None,
    editor_settings: Annotated[
        list[EditorSetting] | None,
        typer.Option(
            "--editor-settings",
            "-es",
            help="Editor settings to configure (vscode, cursor, windsurf, kiro, zed)",
        ),
    ] = None,
    precommit_tool: Annotated[
        PreCommitTool | None,
        typer.Option(
            "--precommit-tools",
            "-pc",
            help="Pre-commit tool to use (lefthook, pre-commit)",
        ),
    ] = None,
) -> None:
    """Initialize Ultrapyup in the current directory."""
    target_path = path.resolve()

    if not target_path.exists():
        log.error(f"Directory does not exist: {target_path}")
        raise typer.Exit(1)

    if not target_path.is_dir():
        log.error(f"Path is not a directory: {target_path}")
        raise typer.Exit(1)

    try:
        with change_directory(target_path):
            initialize(
                package_manager=package_manager,
                editor_rules=editor_rules,
                editor_settings=editor_settings,
                precommit_tool=precommit_tool,
            )
    except Exception as e:
        log.error(f"Initialization failed: {e}")
        raise typer.Exit(1) from e
