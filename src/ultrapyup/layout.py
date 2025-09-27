"""Project layout detection and ty configuration module."""

from enum import Enum
from pathlib import Path
from typing import NamedTuple

import toml


class ProjectLayout(str, Enum):
    """Supported project layout types."""

    SRC_LAYOUT = "src"
    FLAT_LAYOUT = "flat"
    PACKAGE_LAYOUT = "package"
    APP_LAYOUT = "app"
    UNKNOWN = "unknown"


class LayoutDetection(NamedTuple):
    """Result of project layout detection."""

    layout: ProjectLayout
    root_paths: list[str]
    package_name: str | None = None


def _get_project_name() -> str | None:
    """Get project name from pyproject.toml."""
    try:
        pyproject_path = Path("pyproject.toml")
        if not pyproject_path.exists():
            return None

        with open(pyproject_path) as f:
            config = toml.load(f)
            return config.get("project", {}).get("name")
    except Exception:
        return None


def _detect_src_layout() -> LayoutDetection | None:
    """Detect src/ layout pattern."""
    src_path = Path("src")
    if not src_path.exists() or not src_path.is_dir():
        return None

    # Look for packages in src/
    packages = [p for p in src_path.iterdir() if p.is_dir() and not p.name.startswith(".")]

    if packages:
        # Use the first package found as the main package
        main_package = packages[0].name
        return LayoutDetection(
            layout=ProjectLayout.SRC_LAYOUT,
            root_paths=["./src"],
            package_name=main_package,
        )

    return LayoutDetection(
        layout=ProjectLayout.SRC_LAYOUT,
        root_paths=["./src"],
        package_name=None,
    )


def _detect_flat_layout() -> LayoutDetection | None:
    """Detect flat layout pattern (Python files in project root)."""
    root = Path(".")
    python_files = list(root.glob("*.py"))

    if python_files and Path("pyproject.toml").exists():
        return LayoutDetection(
            layout=ProjectLayout.FLAT_LAYOUT,
            root_paths=["./"],
            package_name=None,
        )

    return None


def _detect_package_layout() -> LayoutDetection | None:
    """Detect package layout pattern (package_name/package_name structure)."""
    project_name = _get_project_name()
    if not project_name:
        return None

    # Clean project name (replace hyphens with underscores)
    package_name = project_name.replace("-", "_")
    package_path = Path(package_name)

    if package_path.exists() and package_path.is_dir():
        # Check if it contains Python files
        python_files = list(package_path.glob("**/*.py"))
        if python_files:
            return LayoutDetection(
                layout=ProjectLayout.PACKAGE_LAYOUT,
                root_paths=["./"],
                package_name=package_name,
            )

    return None


def _detect_app_layout() -> LayoutDetection | None:
    """Detect app/ layout pattern."""
    app_path = Path("app")
    if app_path.exists() and app_path.is_dir():
        python_files = list(app_path.glob("**/*.py"))
        if python_files:
            return LayoutDetection(
                layout=ProjectLayout.APP_LAYOUT,
                root_paths=["./app"],
                package_name="app",
            )

    return None


def detect_project_layout() -> LayoutDetection:
    """Detect the project layout and return configuration details.

    Detection order:
    1. src/ layout - most common in modern Python projects
    2. app/ layout - common in web applications
    3. package layout - package_name/package_name structure
    4. flat layout - Python files in project root
    5. unknown - fallback

    Returns:
        LayoutDetection: Detected layout information
    """
    # Try src/ layout first (most common)
    if result := _detect_src_layout():
        return result

    # Try app/ layout
    if result := _detect_app_layout():
        return result

    # Try package layout
    if result := _detect_package_layout():
        return result

    # Try flat layout
    if result := _detect_flat_layout():
        return result

    # Fallback to unknown
    return LayoutDetection(
        layout=ProjectLayout.UNKNOWN,
        root_paths=["./"],
        package_name=None,
    )


def generate_ty_config(layout: LayoutDetection) -> dict:
    """Generate ty configuration based on detected layout.

    Args:
        layout: Detected project layout information

    Returns:
        dict: ty configuration to be added to pyproject.toml
    """
    config = {
        "tool": {
            "ty": {
                "environment": {
                    "root": layout.root_paths,
                }
            }
        }
    }

    # Add common exclusions based on layout
    if layout.layout == ProjectLayout.SRC_LAYOUT:
        config["tool"]["ty"]["src"] = {
            "include": ["src", "tests"],
            "exclude": [
                "tests/fixtures/**",
                "src/**/generated/**",
                "**/__pycache__",
                "**/*.pyc",
            ],
        }
    elif layout.layout == ProjectLayout.APP_LAYOUT:
        config["tool"]["ty"]["src"] = {
            "include": ["app", "tests"],
            "exclude": [
                "tests/fixtures/**",
                "app/**/generated/**",
                "**/__pycache__",
                "**/*.pyc",
            ],
        }
    elif layout.layout == ProjectLayout.PACKAGE_LAYOUT:
        includes = ["tests"]
        if layout.package_name:
            includes.insert(0, layout.package_name)

        config["tool"]["ty"]["src"] = {
            "include": includes,
            "exclude": [
                "tests/fixtures/**",
                f"{layout.package_name}/**/generated/**" if layout.package_name else "**/generated/**",
                "**/__pycache__",
                "**/*.pyc",
            ],
        }
    elif layout.layout == ProjectLayout.FLAT_LAYOUT:
        config["tool"]["ty"]["src"] = {
            "exclude": [
                "tests/fixtures/**",
                "**/generated/**",
                "**/__pycache__",
                "**/*.pyc",
            ],
        }

    # Add common rules configuration
    config["tool"]["ty"]["rules"] = {
        "possibly-unresolved-reference": "warn",
        "unused-ignore-comment": "warn",
        "possibly-unbound-attribute": "error",
        "division-by-zero": "error",
    }

    return config


def apply_ty_config(layout: LayoutDetection) -> None:
    """Apply ty configuration to pyproject.toml based on detected layout.

    Args:
        layout: Detected project layout information
    """
    pyproject_path = Path("pyproject.toml")

    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found")

    # Load existing configuration
    with open(pyproject_path) as f:
        config = toml.load(f)

    # Generate new ty configuration
    ty_config = generate_ty_config(layout)

    # Merge ty configuration
    if "tool" not in config:
        config["tool"] = {}

    config["tool"]["ty"] = ty_config["tool"]["ty"]

    # Write back to file
    with open(pyproject_path, "w") as f:
        toml.dump(config, f)


def get_layout_info(layout: LayoutDetection) -> str:
    """Get human-readable layout information.

    Args:
        layout: Detected project layout information

    Returns:
        str: Formatted layout information
    """
    layout_descriptions = {
        ProjectLayout.SRC_LAYOUT: "Source layout (src/ directory)",
        ProjectLayout.FLAT_LAYOUT: "Flat layout (files in project root)",
        ProjectLayout.PACKAGE_LAYOUT: "Package layout (package_name/package_name structure)",
        ProjectLayout.APP_LAYOUT: "Application layout (app/ directory)",
        ProjectLayout.UNKNOWN: "Unknown layout",
    }

    description = layout_descriptions[layout.layout]
    root_info = f"Root paths: {', '.join(layout.root_paths)}"

    if layout.package_name:
        package_info = f"Main package: {layout.package_name}"
        return f"{description}\n{root_info}\n{package_info}"

    return f"{description}\n{root_info}"
