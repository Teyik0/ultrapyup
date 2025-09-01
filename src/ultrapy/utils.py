from pathlib import Path

from rich.console import Console


console = Console(log_time=False)


class Logger:
    def info(self, message: str):
        console.log(f"[dim grey62]|  {message}\n|[/dim grey62]")

    def title(self, message: str):
        console.log(f"[yellow]◇[/yellow]  {message}")

    def error(self, message: str):
        console.log(f"[red]✗[/red]  {message}")


log = Logger()


def file_exist(path: Path | str):
    if isinstance(path, str):
        path = Path(path)
    return path.exists()
