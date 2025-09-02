import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import toml
from InquirerPy import inquirer

from ultrapyup.utils import console, file_exist, log


if TYPE_CHECKING:
    from ultrapyup.pre_commit import PreCommitTool


@dataclass
class PackageManager:
    """Represents a package manager with its configuration details."""

    name: str
    lockfile: str | None

    def add(self, packages: list[str]) -> None:
        """Add packages using the appropriate package manager.

        Args:
            packages: List of package names to install
        """
        if self.name == "uv":
            self._add_with_uv(packages)
        elif self.name == "pip":
            self._add_with_pip(packages)
        elif self.name == "poetry":
            self._add_with_poetry(packages)
        else:
            raise ValueError(f"Unsupported package manager: {self.name}")

    def _add_with_uv(self, packages: list[str]) -> None:
        """Install packages using uv."""
        cmd = ["uv", "add", *packages, "--dev"]

        result = subprocess.run(cmd, check=False, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to install dependencies: {result.stderr.decode()}")

    def _add_with_poetry(self, packages: list[str]) -> None:
        """Install packages using poetry."""
        cmd = ["poetry", "add", "--group", "dev", *packages]

        result = subprocess.run(cmd, check=False, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to install dependencies: {result.stderr.decode()}")

    def _add_with_pip(self, packages: list[str]) -> None:
        """Install packages using pip."""
        # Determine pip command path
        venv_path = Path(".venv")
        if venv_path.exists():
            pip_cmd = (
                str(Path(".venv") / "Scripts" / "pip")
                if Path(".venv/Scripts").exists()
                else str(Path(".venv") / "bin" / "pip")
            )
        else:
            pip_cmd = "pip"

        self._add_dev_dependencies_to_pyproject(packages, pip_cmd)

    def _add_dev_dependencies_to_pyproject(self, packages: list[str], pip_cmd: str) -> None:  # noqa
        """Add development dependencies to pyproject.toml and install them."""
        # Fetch latest versions from PyPI for each dependency
        latest_versions = {}

        def get_latest_version(lines: list[str]) -> None:
            versions_line = lines[1].split("Available versions:")[1].strip()
            if versions_line:
                # Get the first (latest) version
                latest_version = versions_line.split(",")[0].strip()
                latest_versions[dep] = latest_version
                return

        for dep in packages:
            result = subprocess.run(
                [pip_cmd, "index", "versions", dep],
                check=False,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                get_latest_version(lines)
            else:
                result = subprocess.run(
                    [pip_cmd, "index", "versions", dep, "--pre"],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split("\n")
                    get_latest_version(lines)
                else:
                    latest_versions[dep] = "*"

        # Update pyproject.toml with dev dependencies
        pyproject_path = Path("pyproject.toml")
        with open(pyproject_path) as f:
            config = toml.load(f)
            if "dependency-groups" not in config:
                config["dependency-groups"] = {}

            existing_dev_deps = config["dependency-groups"].get("dev", [])
            existing_packages = set()
            for dep_spec in existing_dev_deps:
                package_name = (
                    dep_spec.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].split("!=")[0].strip()
                )
                existing_packages.add(package_name)

            # Only add NEW packages
            for dep in packages:
                if dep not in existing_packages:
                    version = latest_versions.get(dep, "*")
                    if version != "*":
                        existing_dev_deps.append(f"{dep}>={version}")
                    else:
                        existing_dev_deps.append(dep)

            config["dependency-groups"]["dev"] = existing_dev_deps

        with open(pyproject_path, "w") as f:
            toml.dump(config, f)

        # Install the dependencies
        result = subprocess.run(
            [pip_cmd, "install", "--upgrade", "pip"],
            check=False,
            capture_output=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Failed to upgrade pip: {result.stderr.decode() if result.stderr else 'Unknown error'}")

        result = subprocess.run(
            [pip_cmd, "install", "."],
            check=False,
            capture_output=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to install package: {result.stderr.decode() if result.stderr else 'Unknown error'}"
            )

        result = subprocess.run(
            [pip_cmd, "install", "--group", "dev"],
            check=False,
            capture_output=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to install dev dependencies: {result.stderr.decode() if result.stderr else 'Unknown error'}"
            )


options: list[PackageManager] = [
    PackageManager("uv", "uv.lock"),
    PackageManager("poetry", "poetry.lock"),
    PackageManager("pip", None),
]


def get_package_manager() -> PackageManager:
    """Detect or prompt for package manager selection based on lockfiles or user input."""
    for package_manager in options:
        if package_manager.lockfile and file_exist(Path(package_manager.lockfile)):
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
        transformer=lambda _: "",
    ).execute()

    for pm in options:
        if pm.name == package_manager:
            log.info(package_manager)
            return pm

    raise ValueError(f"Unknown package manager: {package_manager}")


def install_dependencies(package_manager: PackageManager, pre_commit_tools: list["PreCommitTool"] | None) -> None:
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
