from pathlib import Path

from InquirerPy import inquirer

from ultrapyup.package_manager.pm import PackageManager
from ultrapyup.utils import file_exist


options: list[PackageManager] = list(PackageManager)


def _package_manager_ask() -> PackageManager:
    selected_package_manager = inquirer.select(
        message="Which package manager do you use?",
        choices=[package_manager.value for package_manager in options],
        qmark="◆ ",
        amark="◇ ",
        pointer="◼",
        marker="◻",
        marker_pl="  ",
        transformer=lambda _: "",
    ).execute()

    for pm in options:
        if pm.value == selected_package_manager:
            return pm
    raise ValueError(f"Unknown package manager: {selected_package_manager}")


def _package_manager_auto_detect() -> PackageManager | None:
    for package_manager_option in options:
        if package_manager_option.lockfile and file_exist(Path(package_manager_option.lockfile)):
            return package_manager_option
    return None
