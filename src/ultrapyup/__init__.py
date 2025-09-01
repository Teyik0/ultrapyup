from typing import Annotated

import typer

from ultrapyup.initialize import initialize


app = typer.Typer(
    name="Ultrapyup",
    help="Ship code faster and with more confidence.",
    no_args_is_help=True,
)


@app.command("init", help="Initialize Ultrapyup in the current directory")
def init_command():
    initialize()


@app.command("lint", help="Run Ruff linter without fixing files")
def lint_command():
    return


@app.command("format", help="Run Ruff linter and fixes files")
def format_command(
    files: Annotated[
        list[str], typer.Argument(help="specific files to format (optional)")
    ],
    unsafe: bool = typer.Option(False, "--unsafe", help="apply unsafe fixes"),
):
    return
