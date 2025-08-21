import subprocess
from dataclasses import dataclass
from pathlib import Path

import toml
from InquirerPy import inquirer

from ultrapy.pre_commit import PreCommitTool
from ultrapy.utils import console, file_exist, log


@dataclass
class PackageManager:
    name: str
    add_cmd: str
    lockfile: str


options: list[PackageManager] = [
    PackageManager("uv", "uv add", "uv.lock"),
    PackageManager("pip", "pip install", "requirements.txt"),
]


def get_package_manager() -> PackageManager:
    for package_manager in options:
        if file_exist(Path(package_manager.lockfile)):
            log.title("Package manager auto detected")
            log.info(package_manager.name)
            return package_manager

    package_manager = inquirer.select(
        message="Which package manager do you use?",
        choices=[package_manager.name for package_manager in options],
        qmark="◆ ",
        amark="◇ ",
        pointer="◼",
        marker="◻",
        marker_pl="  ",
        transformer=lambda result: "",
    ).execute()

    for pm in options:
        if pm.name == package_manager:
            log.info(package_manager)
            return pm

    raise ValueError(f"Unknown package manager: {package_manager}")


def install_dependencies(
    package_manager: PackageManager, pre_commit_tools: list[PreCommitTool] | None
):
    with console.status("[bold green]Installing dependencies"):
        subprocess.run(
            f"{package_manager.add_cmd} ruff ty ultrapy"
            f"{
                ' '.join(precommit_tool.value for precommit_tool in pre_commit_tools)
                if pre_commit_tools
                else ' '
            } --dev",
            shell=True,
            capture_output=True,
        )
        log.title("Dependencies installed")
        log.info(
            f"ruff, ty{', ' if pre_commit_tools else ''}{
                ', '.join(precommit_tool.value for precommit_tool in pre_commit_tools)
                if pre_commit_tools
                else ''
            }"
        )


def ruff_config_setup():
    """Add Ruff configuration to pyproject.toml that extends the base configuration from local .venv ultrapy installation."""
    pyproject_path = Path.cwd() / "pyproject.toml"

    if not pyproject_path.exists():
        log.info("No pyproject.toml found, skipping Ruff configuration")
        return

    # Read existing pyproject.toml
    try:
        with open(pyproject_path) as f:
            config = toml.load(f)
    except Exception as e:
        log.info(f"Could not read pyproject.toml: {e}")
        return

    # Check if Ruff configuration already exists
    ruff_exists = "tool" in config and "ruff" in config["tool"]

    # Use relative path to ultrapy's base configuration in .venv
    base_config_path = (
        ".venv/lib/python*/site-packages/ultrapy/resources/ruff_base.toml"
    )

    # Read the current file content
    current_content = pyproject_path.read_text()

    if ruff_exists:
        # Replace existing [tool.ruff] section
        import re

        # Pattern to match [tool.ruff] section and everything until next [section]
        pattern = r"\[tool\.ruff\].*?(?=\n\[|\Z)"
        updated_content = re.sub(
            pattern,
            f'[tool.ruff]\nextend = "{base_config_path}"',
            current_content,
            flags=re.DOTALL,
        )
    else:
        # Append to the file
        ruff_config = f"""
[tool.ruff]
extend = "{base_config_path}"
"""
        updated_content = current_content + ruff_config

    pyproject_path.write_text(updated_content)

    log.title("Ruff configuration setup completed")
    action = "Overrode" if ruff_exists else "Added"
    log.info(f"{action} Ruff config in pyproject.toml (extends {base_config_path})")
