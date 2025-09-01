import subprocess
from dataclasses import dataclass
from pathlib import Path

import toml
from InquirerPy import inquirer

from ultrapyup.pre_commit import PreCommitTool
from ultrapyup.utils import console, file_exist, log


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


def _install_with_uv(package_manager: PackageManager, dev_deps: list[str]):
    """Install dependencies using uv package manager."""
    result = subprocess.run(
        f"{package_manager.add_cmd} {' '.join(dev_deps)} --dev",
        shell=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to install dependencies: {result.stderr.decode()}")


def _install_with_pip(package_manager: PackageManager, dev_deps: list[str]):
    """Install dependencies using pip package manager."""
    venv_path = Path(".venv")
    if venv_path.exists():
        pip_cmd = (
            ".venv/bin/pip"
            if not Path(".venv/Scripts").exists()
            else ".venv/Scripts/pip"
        )
    else:
        pip_cmd = "pip"

    # Fetch latest versions from PyPI for each dependency
    latest_versions = {}
    for dep in dev_deps:
        result = subprocess.run(
            f"{pip_cmd} index versions {dep}",
            shell=True,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            versions_line = lines[1].split("Available versions:")[1].strip()
            if versions_line:
                # Get the first (latest) version
                latest_version = versions_line.split(",")[0].strip()
                latest_versions[dep] = latest_version
                break
        else:
            latest_versions[dep] = "*"

    # Update pyproject.toml with dev dependencies using toml library
    pyproject_path = Path("pyproject.toml")
    with open(pyproject_path) as f:
        config = toml.load(f)
        if "dependency-groups" not in config:
            config["dependency-groups"] = {}

        existing_dev_deps = config["dependency-groups"].get("dev", [])
        existing_packages = set()
        for dep_spec in existing_dev_deps:
            package_name = (
                dep_spec.split("==")[0]
                .split(">=")[0]
                .split("<=")[0]
                .split("~=")[0]
                .split("!=")[0]
                .strip()
            )
            existing_packages.add(package_name)

        merged_dev_deps = []

        for dep_spec in existing_dev_deps:
            package_name = (
                dep_spec.split("==")[0]
                .split(">=")[0]
                .split("<=")[0]
                .split("~=")[0]
                .split("!=")[0]
                .strip()
            )
            if package_name not in dev_deps:
                merged_dev_deps.append(dep_spec)

        for dep in dev_deps:
            version = latest_versions.get(dep, "*")
            if version != "*":
                merged_dev_deps.append(f"{dep}=={version}")
            else:
                merged_dev_deps.append(dep)

        config["dependency-groups"]["dev"] = merged_dev_deps

    with open(pyproject_path, "w") as f:
        toml.dump(config, f)

    result = subprocess.run(
        f"{pip_cmd} install -e .",
        shell=True,
    )
    if result.returncode != 0:
        log.info(f"pip install -e . failed with return code {result.returncode}")


def install_dependencies(
    package_manager: PackageManager, pre_commit_tools: list[PreCommitTool] | None
) -> None:
    dev_deps = ["ruff", "ty", "ultrapyup"]
    if pre_commit_tools:
        dev_deps.extend(precommit_tool.value for precommit_tool in pre_commit_tools)

    with console.status("[bold green]Installing dependencies"):
        if package_manager.name == "uv":
            _install_with_uv(package_manager, dev_deps)
        else:
            _install_with_pip(package_manager, dev_deps)

        log.title("Dependencies installed")
        log.info(
            f"ruff, ty, ultrapyup{', ' if pre_commit_tools else ''}{
                ', '.join(precommit_tool.value for precommit_tool in pre_commit_tools)
                if pre_commit_tools
                else ''
            }"
        )


def ruff_config_setup():
    """Add Ruff configuration to pyproject.toml that extends the base configuration from local .venv ultrapyup installation."""
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
            "No virtualenv site-packages directory found. Please ensure your virtual environment is properly initialized."
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


def ty_config_setup():
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
    action = "Override" if ty_exists else "Added"
    log.info(f"{action} Ty config in pyproject.toml with root=['./src']")
