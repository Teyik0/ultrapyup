import typer
from format import format as format_cmd
from initialize import initialize
from lint import lint

app = typer.Typer(name="Ultrapy", help="Ship code faster and with more confidence.")


@app.command("init", help="Initialize Ultrapy in the current directory")
def init_command():
    initialize()


@app.command("lint", help="Run Ruff linter without fixing files")
def lint_command(
    files: list[str] = typer.Argument(None, help="specific files to lint (optional)"),
):
    lint(files)


@app.command("format", help="Run Ruff linter and fixes files")
def format_command(
    files: list[str] = typer.Argument(None, help="specific files to format (optional)"),
    unsafe: bool = typer.Option(False, "--unsafe", help="apply unsafe fixes"),
):
    format_cmd(files, unsafe)


if __name__ == "__main__":
    app()
