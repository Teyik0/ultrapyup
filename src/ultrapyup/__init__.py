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


@app.command("init", help="Initialize Ultrapyup in the current directory")
def init_command(
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
    precommit_tools: Annotated[
        list[PreCommitTool] | None,
        typer.Option(
            "--precommit-tools",
            "-pc",
            help="Pre-commit tools to use (lefthook, pre-commit)",
        ),
    ] = None,
) -> None:
    """Initialize Ultrapyup in the current directory."""
    try:
        initialize(
            package_manager=package_manager,
            editor_rules=editor_rules,
            editor_settings=editor_settings,
            precommit_tools=precommit_tools,
        )
    except Exception as e:
        log.error(f"Initialization failed: {e}")


@app.command("lint", help="Run Ruff linter without fixing files")
def lint_command() -> None:
    """Run Ruff linter without fixing files."""
    return


@app.command("format", help="Run Ruff linter and fixes files")
def format_command(
    files: Annotated[list[str], typer.Argument(help="specific files to format (optional)")],  # noqa: ARG001
    unsafe: bool = typer.Option(False, "--unsafe", help="apply unsafe fixes"),  # noqa: ARG001, FBT001
) -> None:
    """Run Ruff linter and fixes files."""
    return
