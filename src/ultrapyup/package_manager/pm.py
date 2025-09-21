import subprocess
from enum import Enum
from pathlib import Path

import toml


class PackageManager(str, Enum):
    """Package manager options with integrated functionality."""

    UV = "uv"
    POETRY = "poetry"
    PIP = "pip"
    SKIP = "skip"

    @property
    def lockfile(self) -> str | None:
        """Get the lockfile associated with this package manager."""
        if self == PackageManager.SKIP:
            raise ValueError("Cannot get lockfile for SKIP package manager")
        lockfile_map = {
            "uv": "uv.lock",
            "poetry": "poetry.lock",
            "pip": None,
        }
        return lockfile_map[self.value]

    def add(self, packages: list[str]) -> None:
        """Add packages using the appropriate package manager.

        Args:
            packages: List of package names to install
        """
        match self:
            case PackageManager.UV:
                self._add_with_uv(packages)
            case PackageManager.PIP:
                self._add_with_pip(packages)
            case PackageManager.POETRY:
                self._add_with_poetry(packages)
            case PackageManager.SKIP:
                raise NotImplementedError("Cannot add packages when package manager is set to SKIP")

    def _add_with_uv(self, packages: list[str]) -> None:
        """Install packages using uv."""
        cmd = ["uv", "add", *packages, "--dev"]

        result = subprocess.run(cmd, check=False, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to install dev dependencies: {result.stderr.decode()}")

    def _add_with_poetry(self, packages: list[str]) -> None:
        """Install packages using poetry."""
        cmd = ["poetry", "add", "--group", "dev", *packages]

        result = subprocess.run(cmd, check=False, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to install dev dependencies: {result.stderr.decode()}")

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
