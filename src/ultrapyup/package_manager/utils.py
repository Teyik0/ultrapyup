from pathlib import Path

from ultrapyup.package_manager.pm import PackageManager
from ultrapyup.precommit import PreCommitTool
from ultrapyup.utils import ask, console, file_exist, log


options: list[PackageManager] = [pm for pm in PackageManager if pm != PackageManager.SKIP]


def _package_manager_ask() -> PackageManager:
    selected_package_manager = ask(
        msg="Which package manager do you use?",
        choices=[package_manager.value for package_manager in options],
        multiselect=False,
    )

    for pm in options:
        if pm.value == selected_package_manager:
            return pm
    raise ValueError(f"Unknown package manager: {selected_package_manager}")


def _package_manager_auto_detect() -> PackageManager | None:
    for package_manager_option in options:
        if package_manager_option.lockfile and file_exist(Path(package_manager_option.lockfile)):
            return package_manager_option
    return None


def install_dependencies(package_manager: PackageManager, precommit_tool: PreCommitTool | None) -> None:
    """Install development dependencies using the specified package manager."""
    dev_deps = ["ruff", "ty"]
    if precommit_tool:
        dev_deps.append(precommit_tool.value)

    with console.status("[bold green]Installing dependencies"):
        package_manager.add(dev_deps)

        log.title("Dependencies installed")
        log.info(f"ruff, ty{f', {precommit_tool.value}' if precommit_tool else ''}")
