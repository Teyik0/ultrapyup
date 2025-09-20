from pathlib import Path
from typing import Any

import toml

from ultrapyup.utils import log


class RuffConfigError(Exception):
    """Exception raised when Ruff configuration fails."""


def _load_pyproject_toml(pyproject_path: Path) -> dict[str, Any]:
    """Load and parse pyproject.toml file.

    Args:
        pyproject_path: Path to pyproject.toml file

    Returns:
        dict: Parsed TOML configuration

    Raises:
        RuffConfigError: If file cannot be read or parsed
    """
    try:
        with open(pyproject_path) as f:
            return toml.load(f)
    except Exception as e:
        raise RuffConfigError(f"Could not read pyproject.toml: {e}") from e


def _save_pyproject_toml(pyproject_path: Path, config: dict[str, Any]) -> None:
    """Save configuration to pyproject.toml file.

    Args:
        pyproject_path: Path to pyproject.toml file
        config: Configuration data to save

    Raises:
        RuffConfigError: If file cannot be written
    """
    try:
        with open(pyproject_path, "w") as f:
            toml.dump(config, f)
    except Exception as e:
        raise RuffConfigError(f"Could not write pyproject.toml: {e}") from e


def _find_site_packages_path() -> Path | None:
    """Find the site-packages directory in the virtual environment.

    Returns:
        Path to site-packages directory or None if not found
    """
    # Try Linux/macOS variants first
    for lib_dir in [".venv/lib", ".venv/lib64"]:
        venv_lib_path = Path(lib_dir)
        if not (venv_lib_path.exists() and venv_lib_path.is_dir()):
            continue

        # Find python* directory (pythonX or pythonX.Y patterns)
        python_dirs = list(venv_lib_path.glob("python*"))
        for python_dir in python_dirs:
            if not python_dir.is_dir():
                continue

            candidate_path = python_dir / "site-packages"
            if candidate_path.exists() and candidate_path.is_dir():
                return candidate_path

    # Try Windows variant if Linux/macOS paths not found
    windows_path = Path(".venv/Lib/site-packages")
    if windows_path.exists() and windows_path.is_dir():
        return windows_path

    return None


def _get_base_config_path() -> str:
    """Get the path to the base Ruff configuration file.

    Returns:
        str: Path to ruff_base.toml in ultrapyup resources

    Raises:
        RuffConfigError: If site-packages directory cannot be found
    """
    site_packages_path = _find_site_packages_path()

    if not site_packages_path:
        raise RuffConfigError(
            "No virtualenv site-packages directory found. Please ensure your "
            "virtual environment is properly initialized."
        )

    return str(site_packages_path / "ultrapyup/resources/ruff_base.toml")


def _has_existing_ruff_config(config: dict[str, Any]) -> bool:
    """Check if Ruff configuration already exists in the config.

    Args:
        config: Parsed pyproject.toml configuration

    Returns:
        bool: True if Ruff config exists, False otherwise
    """
    return "tool" in config and "ruff" in config["tool"]


def _update_ruff_config(config: dict[str, Any], base_config_path: str) -> None:
    """Update the configuration with Ruff settings.

    Args:
        config: Configuration dictionary to update
        base_config_path: Path to base Ruff configuration
    """
    if "tool" not in config:
        config["tool"] = {}

    config["tool"]["ruff"] = {"extend": base_config_path}


def ruff_config_setup() -> None:
    """Set up Ruff configuration by extending base config from ultrapyup installation.

    This function:
    1. Checks for existing pyproject.toml file
    2. Loads current configuration
    3. Finds the ultrapyup base configuration in site-packages
    4. Updates Ruff config to extend the base configuration
    5. Saves the updated configuration

    Raises:
        RuffConfigError: If configuration setup fails
    """
    pyproject_path = Path.cwd() / "pyproject.toml"

    if not pyproject_path.exists():
        log.info("No pyproject.toml found, skipping Ruff configuration")
        return

    try:
        # Load existing configuration
        config = _load_pyproject_toml(pyproject_path)

        # Check if Ruff config already exists
        ruff_exists = _has_existing_ruff_config(config)

        # Get base configuration path
        base_config_path = _get_base_config_path()

        # Update Ruff configuration
        _update_ruff_config(config, base_config_path)

        # Save updated configuration
        _save_pyproject_toml(pyproject_path, config)

        # Log success
        log.title("Ruff configuration setup completed")
        action = "Override" if ruff_exists else "Added"
        log.info(f"{action} Ruff config in pyproject.toml (extends {base_config_path})")

    except RuffConfigError as e:
        log.info(str(e))
    except Exception as e:
        log.info(f"Unexpected error during Ruff configuration: {e}")
