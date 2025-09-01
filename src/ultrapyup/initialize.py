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


def _migrate_requirements_to_pyproject() -> None:
    """Migrate requirements.txt to pyproject.toml if needed."""
    requirements_path = Path("requirements.txt")
    pyproject_path = Path("pyproject.toml")

    if not requirements_path.exists() or pyproject_path.exists():
        return

    requirements = requirements_path.read_text().strip().split("\n")
    requirements = [
        req.strip() for req in requirements if req.strip() and not req.startswith("#")
    ]

    pyproject_content = f"""[project]
name = "your-project-name"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
{chr(10).join(f'    "{req}",' for req in requirements)}
]

[build-system]
requires = ["uv_build>=0.8.0,<0.9"]
build-backend = "uv_build"
"""

    pyproject_path.write_text(pyproject_content)
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

    _migrate_requirements_to_pyproject()

    return True


def initialize():
    if not _check_python_project():
        return

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
            precommit_setup(package_manager.add_cmd, tool)
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
