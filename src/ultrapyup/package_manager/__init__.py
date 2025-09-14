from ultrapyup.package_manager.pm import PackageManager
from ultrapyup.package_manager.utils import (
    _package_manager_ask,
    _package_manager_auto_detect,
    options,
)
from ultrapyup.utils import log


def get_package_manager(package_manager: PackageManager | None = None) -> PackageManager:
    """Detect or prompt for package manager selection based on lockfiles or user input."""
    if package_manager:
        log.title("Package manager selected")
        log.info(package_manager.value)
        return package_manager
    elif detected_pm := _package_manager_auto_detect():
        log.title("Package manager auto detected")
        log.info(detected_pm.value)
        return detected_pm
    else:
        pm = _package_manager_ask()
        log.info(pm.value)
        return pm


__all__ = ["PackageManager", "options"]
