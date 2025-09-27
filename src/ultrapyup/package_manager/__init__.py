from ultrapyup.package_manager.pm import PackageManager
from ultrapyup.package_manager.utils import (
    _package_manager_ask,
    _package_manager_auto_detect,
    install_dependencies,
    options,
)
from ultrapyup.utils import log


def get_package_manager(package_manager: PackageManager | None = None) -> PackageManager:
    """Detect or prompt for package manager selection based on lockfiles or user input."""
    # Explicit package manager provided
    if package_manager is not None and package_manager.value != "skip":
        log.title("Package manager selected")
        log.info(package_manager.value)
        return package_manager

    # Try auto-detection (works for both "skip" and None cases)
    if detected_pm := _package_manager_auto_detect():
        log.title("Package manager auto detected")
        log.info(detected_pm.value)
        return detected_pm

    # Ask user if not provided
    if package_manager is None:
        pm = _package_manager_ask()
        if pm.value == "skip":
            raise RuntimeError("Unable to auto detect your package manager, specify one.")
        log.info(pm.value)
        return pm

    # Handle fallback cases
    raise RuntimeError("Unable to auto detect your package manager, specify one.")


__all__ = ["PackageManager", "install_dependencies", "options"]
