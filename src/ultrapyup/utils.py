from pathlib import Path

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


def file_exist(path: Path | str) -> bool:
    """Check if a file or directory exists at the given path."""
    if isinstance(path, str):
        path = Path(path)
    return path.exists()
