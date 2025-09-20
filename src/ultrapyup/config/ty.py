"""Ty configuration module for Python type checking setup."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import toml

from ultrapyup.layout import LayoutDetection, ProjectLayout, apply_ty_config, detect_project_layout
from ultrapyup.utils import log


class TyConfigError(Exception):
    """Exception raised when Ty configuration fails."""

    def __init__(self, message: str, *, cause: Exception | None = None) -> None:
        """Initialize TyConfigError.

        Args:
            message: Error message
            cause: Optional underlying exception
        """
        super().__init__(message)
        self.cause = cause


@dataclass
class TyConfigResult:
    """Result of Ty configuration setup."""

    success: bool
    layout_detected: LayoutDetection | None = None
    config_exists: bool = False
    fallback_used: bool = False
    error_message: str | None = None


def _check_pyproject_exists(pyproject_path: Path) -> None:
    """Check if pyproject.toml exists and raise error if not.

    Args:
        pyproject_path: Path to pyproject.toml

    Raises:
        TyConfigError: If pyproject.toml doesn't exist
    """
    if not pyproject_path.exists():
        raise TyConfigError("No pyproject.toml found")


def _load_pyproject_config(pyproject_path: Path) -> dict:
    """Load configuration from pyproject.toml.

    Args:
        pyproject_path: Path to pyproject.toml

    Returns:
        dict: Loaded configuration

    Raises:
        TyConfigError: If config cannot be loaded
    """
    # Check if file is readable
    if not pyproject_path.is_file():
        raise TyConfigError(f"pyproject.toml is not a valid file: {pyproject_path}")

    # Check if file has content (allow empty files for fallback config)
    if pyproject_path.stat().st_size == 0:
        # Return empty dict for empty files - let caller handle it
        return {}

    # Load TOML content - let toml.load raise its own exceptions
    with pyproject_path.open() as f:
        config = toml.load(f)

    # Validate that we got a dictionary
    if not isinstance(config, dict):
        raise TyConfigError("Invalid pyproject.toml format - expected dictionary")

    return config


def _check_ty_config_exists(config: dict) -> bool:
    """Check if Ty configuration already exists.

    Args:
        config: Loaded pyproject.toml configuration

    Returns:
        bool: True if Ty config exists
    """
    return "tool" in config and "ty" in config["tool"]


def _apply_fallback_config(pyproject_path: Path) -> None:
    """Apply fallback Ty configuration.

    Args:
        pyproject_path: Path to pyproject.toml

    Raises:
        TyConfigError: If fallback config cannot be applied
    """
    config = _load_pyproject_config(pyproject_path)

    if "tool" not in config:
        config["tool"] = {}

    config["tool"]["ty"] = {
        "environment": {"root": ["./src"]},
        "rules": {
            "possibly-unresolved-reference": "warn",
            "unused-ignore-comment": "warn",
            "possibly-unbound-attribute": "error",
            "division-by-zero": "error",
        },
        "src": {
            "exclude": [
                "tests/fixtures/**",
                "**/generated/**",
                "**/__pycache__",
                "**/*.pyc",
            ]
        },
    }

    # Check if we can write to the file
    if not pyproject_path.parent.exists():
        raise TyConfigError(f"Parent directory does not exist: {pyproject_path.parent}")

    # Write configuration back to file
    with pyproject_path.open("w") as f:
        toml.dump(config, f)


def _log_success_info(layout: LayoutDetection) -> None:
    """Log successful configuration information.

    Args:
        layout: Detected project layout
    """
    log.title("Ty configuration setup completed")
    log.info(f"Detected layout: {layout.layout.value}")
    log.info(f"Root paths: {', '.join(layout.root_paths)}")
    if layout.package_name:
        log.info(f"Main package: {layout.package_name}")


def ty_config_setup() -> TyConfigResult:
    """Configure Ty based on detected project layout.

    This function:
    1. Checks for pyproject.toml existence
    2. Verifies if Ty configuration already exists
    3. Detects project layout
    4. Applies appropriate Ty configuration
    5. Falls back to basic configuration if detection fails

    Returns:
        TyConfigResult: Result of the configuration setup
    """
    pyproject_path = Path.cwd() / "pyproject.toml"

    # Check if pyproject.toml exists
    if not pyproject_path.exists():
        log.info("No pyproject.toml found, skipping Ty configuration")
        return TyConfigResult(success=False, error_message="No pyproject.toml found")

    # Load existing configuration - if this fails, let it raise
    config = _load_pyproject_config(pyproject_path)

    # Check if Ty configuration already exists
    if _check_ty_config_exists(config):
        log.info("Ty configuration already exists, skipping")
        return TyConfigResult(success=True, config_exists=True)

    # Detect project layout
    layout = detect_project_layout()

    # If layout detection succeeds, apply it
    if layout and layout.layout != ProjectLayout.UNKNOWN:
        apply_ty_config(layout)
        _log_success_info(layout)
        return TyConfigResult(success=True, layout_detected=layout)

    # If detection failed or returned unknown, apply fallback
    log.error("Failed to detect project layout or layout is unknown, applying fallback")
    _apply_fallback_config(pyproject_path)
    log.info("Applied fallback Ty configuration")

    return TyConfigResult(success=True, fallback_used=True)


def validate_ty_config() -> bool:
    """Validate existing Ty configuration.

    Returns:
        bool: True if configuration is valid
    """
    pyproject_path = Path.cwd() / "pyproject.toml"

    if not pyproject_path.exists():
        return False

    # Load config - if this fails, return False (invalid)
    config = _load_pyproject_config(pyproject_path)

    if not _check_ty_config_exists(config):
        return False

    ty_config = config["tool"]["ty"]

    # Basic validation - check required sections
    required_sections = ["environment"]
    return all(section in ty_config for section in required_sections)


def get_ty_config_info() -> dict | None:
    """Get information about current Ty configuration.

    Returns:
        dict | None: Configuration info or None if not found
    """
    pyproject_path = Path.cwd() / "pyproject.toml"

    if not pyproject_path.exists():
        return None

    # Load config - if this fails, return None
    config = _load_pyproject_config(pyproject_path)

    if not _check_ty_config_exists(config):
        return None

    return config["tool"]["ty"]
