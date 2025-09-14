from pathlib import Path

import toml

from ultrapyup.package_manager import PackageManager
from ultrapyup.precommit import PreCommitTool
from ultrapyup.utils import console, log


def install_dependencies(package_manager: PackageManager, pre_commit_tools: list[PreCommitTool] | None) -> None:
    """Install development dependencies using the specified package manager."""
    dev_deps = ["ruff", "ty", "ultrapyup"]
    if pre_commit_tools:
        dev_deps.extend(precommit_tool.value for precommit_tool in pre_commit_tools)

    with console.status("[bold green]Installing dependencies"):
        package_manager.add(dev_deps)

        log.title("Dependencies installed")
        log.info(
            f"ruff, ty, ultrapyup{', ' if pre_commit_tools else ''}{
                ', '.join(precommit_tool.value for precommit_tool in pre_commit_tools) if pre_commit_tools else ''
            }"
        )


def ruff_config_setup() -> None:  # noqa: C901
    """Extends ruff base configuration from local .venv ultrapyup user installation."""
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

    # Detect Python version in .venv - try cross-platform paths
    site_packages_path = None

    # Try Linux/macOS variants first
    for lib_dir in [".venv/lib", ".venv/lib64"]:
        venv_lib_path = Path(lib_dir)
        if venv_lib_path.exists() and venv_lib_path.is_dir():
            # Find python* directory (pythonX or pythonX.Y patterns)
            python_dirs = list(venv_lib_path.glob("python*"))
            for python_dir in python_dirs:
                if python_dir.is_dir():
                    candidate_path = python_dir / "site-packages"
                    if candidate_path.exists() and candidate_path.is_dir():
                        site_packages_path = candidate_path
                        break
        if site_packages_path:
            break

    # Try Windows variant if Linux/macOS paths not found
    if not site_packages_path:
        windows_path = Path(".venv/Lib/site-packages")
        if windows_path.exists() and windows_path.is_dir():
            site_packages_path = windows_path

    # If no valid site-packages found, return with clear message
    if not site_packages_path:
        log.info(
            "No virtualenv site-packages directory found. Please ensure your "
            "virtual environment is properly initialized."
        )
        return

    base_config_path = str(site_packages_path / "ultrapyup/resources/ruff_base.toml")

    # Update or add Ruff configuration using toml library
    with open(pyproject_path) as f:
        config = toml.load(f)

        if "tool" not in config:
            config["tool"] = {}

        config["tool"]["ruff"] = {"extend": base_config_path}

    with open(pyproject_path, "w") as f:
        toml.dump(config, f)

    log.title("Ruff configuration setup completed")
    action = "Override" if ruff_exists else "Added"
    log.info(f"{action} Ruff config in pyproject.toml (extends {base_config_path})")


def ty_config_setup() -> None:
    """Add Ty configuration to pyproject.toml with basic root configuration."""
    pyproject_path = Path.cwd() / "pyproject.toml"

    if not pyproject_path.exists():
        log.info("No pyproject.toml found, skipping Ty configuration")
        return

    with open(pyproject_path) as f:
        config = toml.load(f)
        ty_exists = "tool" in config and "ty" in config["tool"]
        if not ty_exists:
            config["tool"]["ty"] = {"environment": {"root": ["./src"]}}

    with open(pyproject_path, "w") as f:
        toml.dump(config, f)

    log.title("Ty configuration setup completed")
    log.info("Added Ty config in pyproject.toml with root=['./src']")
