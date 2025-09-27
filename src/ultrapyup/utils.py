from pathlib import Path

from InquirerPy import inquirer
from rich.console import Console


console = Console(log_time=False)


class Logger:
    """A logger class for formatted console output."""

    def info(self, message: str) -> None:
        """Log an informational message with grey formatting."""
        console.log(f"[dim grey62]|  {message}\n|[/dim grey62]")

    def title(self, message: str) -> None:
        """Log a title message with yellow formatting."""
        console.log(f"[yellow]◇[/yellow]  {message}")

    def error(self, message: str) -> None:
        """Log an error message with red formatting."""
        console.log(f"[red]✗[/red]  {message}")


log = Logger()


def log_selection(items: list | None, title: str) -> None:
    """Helper to log selected items."""
    log.title(title)
    if items:
        log.info(", ".join(item.value for item in items))
    else:
        log.info("none")


def log_info_only(items: list | None) -> None:
    """Helper to log selected items without title."""
    if items:
        log.info(", ".join(item.value for item in items))
    else:
        log.info("none")


def file_exist(path: Path | str) -> bool:
    """Check if a file or directory exists at the given path."""
    if isinstance(path, str):
        path = Path(path)
    return path.exists()


def ask(msg: str, choices: list[str], multiselect: bool) -> list[str]:  # noqa: FBT001
    """Prompt the user to select multiple options from a list."""
    values = inquirer.select(
        message=msg,
        choices=choices,
        multiselect=multiselect,
        qmark="◆ ",
        amark="◇ ",
        pointer="◼ ",
        marker="◻ ",
        marker_pl=" ",
        transformer=lambda _: "",
        keybindings={
            "skip": [{"key": "c-c"}],
        },
        mandatory=False,
    ).execute()
    return values
