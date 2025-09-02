"""Module for project initialization and configuration."""

import sys
from pathlib import Path

from ultrapyup.editor import editor_setup, get_editors
from ultrapyup.package_manager import (
    get_package_manager,
    install_dependencies,
    ruff_config_setup,
    ty_config_setup,
)
from ultrapyup.pre_commit import get_precommit_tool, precommit_setup
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


def initialize() -> None:
    """Initialize and configure a Python project with development tools."""
    if not _check_python_project():
        return

    # Migrate requirements.txt to pyproject.toml if needed
    _migrate_requirements_to_pyproject()

    # Ask user's preferences
    package_manager = get_package_manager()
    editors = get_editors()
    pre_commit_tools = get_precommit_tool()

    # Configure user's experience
    install_dependencies(package_manager, pre_commit_tools)
    ruff_config_setup()
    ty_config_setup()

    if pre_commit_tools:
        for tool in pre_commit_tools:
            precommit_setup(package_manager, tool)
        log.title("Pre-commit setup completed")
        log.info(f"{', '.join(tool.filename for tool in pre_commit_tools)} created")

    if editors:
        for editor in editors:
            editor_setup(editor)
        log.title("Editor setup completed")
        log.info(
            f"{', '.join(editor.file for editor in editors)}, "
            f"{', '.join(editor.rule_file for editor in editors)} created"
        )

    return
