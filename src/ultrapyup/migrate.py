import sys
from pathlib import Path

from ultrapyup.utils import file_exist, log


def _get_python_version() -> str:
    """Get the current Python version in format 'X.Y'."""
    return f"{sys.version_info.major}.{sys.version_info.minor}"


def _migrate_requirements_to_pyproject() -> None:
    """Migrate requirements.txt to pyproject.toml if needed."""
    requirements_path = Path("requirements.txt")
    pyproject_path = Path("pyproject.toml")

    if not requirements_path.exists() or pyproject_path.exists():
        return

    requirements = requirements_path.read_text().strip().split("\n")
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith("#")]

    filtered_requirements = [
        req for req in requirements if not any(keyword in req.lower() for keyword in ["ruff", "ty", "lefthook"])
    ]
    # Build dependency lines with proper formatting (no trailing comma)
    dependency_lines = [f'    "{req}"' for req in filtered_requirements]
    dependencies_content = ",\n".join(dependency_lines)

    python_version = _get_python_version()
    pyproject_content = f"""[project]
name = "your-project-name"
version = "0.1.0"
description = "Add your description here"
requires-python = ">={python_version}"
dependencies = [
{dependencies_content}
]
"""

    pyproject_path.write_text(pyproject_content)
    requirements_path.unlink()
    log.title("📦 Migrated requirements.txt to pyproject.toml")
    log.info(f"Found {len(requirements)} dependencies")
    log.info("Please update project name and version in pyproject.toml")


def _check_python_project() -> bool:
    """Check if current directory contains a Python project.

    Returns:
        bool: True if Python project detected, False otherwise
    """
    project_files = [
        Path(".venv"),
        Path("requirements.txt"),
        Path("pyproject.toml"),
    ]

    if not any(file_exist(file) for file in project_files):
        log.title("🛑 No Python project detected")
        log.info("Please initialize a Python project first with: uv init")
        return False

    return True
