from pathlib import Path

import pytest
import toml

from ultrapyup.initialize import _migrate_requirements_to_pyproject
from ultrapyup.package_manager.pm import PackageManager


class TestPackageManager:
    """Tests for PackageManager Enum class."""

    def test_package_manager_enum_values(self) -> None:
        """Test PackageManager enum values."""
        assert PackageManager.UV.value == "uv"
        assert PackageManager.POETRY.value == "poetry"
        assert PackageManager.PIP.value == "pip"

    def test_package_manager_lockfile_property(self) -> None:
        """Test lockfile property for each package manager."""
        assert PackageManager.UV.lockfile == "uv.lock"
        assert PackageManager.POETRY.lockfile == "poetry.lock"
        assert PackageManager.PIP.lockfile is None


def assert_deps_updated(deps: list[str], pm: PackageManager) -> None:
    """Helper to assert pyproject.toml was updated with dev dependencies."""
    pyproject_path = Path("pyproject.toml")

    assert pyproject_path.exists()
    if pm.lockfile:
        assert Path(pm.lockfile).exists()

    with open(pyproject_path) as f:
        config = toml.load(f)

    if pm.value in {"pip", "uv"}:
        dev_deps = config.get("dependency-groups", {}).get("dev", [])
    else:  # poetry
        dev_deps = (
            config.get("tool", {}).get("poetry", {}).get("group", {}).get("dev", {}).get("dependencies", {}).keys()
        )
    for dep in deps:
        dep_found = any(dep in dev_dep for dev_dep in dev_deps)
        assert dep_found, f"Dependency '{dep}' not found in dev dependencies"


class TestPackageManagerUV:
    """Tests for PackageManager UV functionality."""

    def test_add_with_uv_success(self, python_uv_project: Path) -> None:  # noqa: ARG002
        """Test successful package installation with uv."""
        pm = PackageManager.UV
        deps = ["pytest"]
        pm.add(deps)
        assert_deps_updated(deps, pm)

    def test_add_with_uv_failure(self, python_uv_project: Path) -> None:  # noqa: ARG002
        """Test package installation failure with uv."""
        pm = PackageManager.UV
        with pytest.raises(RuntimeError, match="Failed to install dev dependencies"):
            pm.add(["non-existent-package-12345"])


class TestPackageManagerPoetry:
    """Tests for PackageManager Poetry functionality."""

    def test_add_with_poetry_success(self, python_poetry_project: Path) -> None:  # noqa: ARG002
        """Test successful package installation with poetry."""
        pm = PackageManager.POETRY

        deps = ["pytest"]
        pm.add(deps)
        assert_deps_updated(deps, pm)

    def test_add_with_poetry_failure(self, python_poetry_project: Path) -> None:  # noqa: ARG002
        """Test package installation failure with poetry."""
        pm = PackageManager.POETRY
        with pytest.raises(RuntimeError, match="Failed to install dev dependencies"):
            pm.add(["non-existent-package-12345"])


class TestPackageManagerPip:
    """Tests for PackageManager Pip functionality."""

    def test_add_with_pip_success(self, python_pip_project: Path) -> None:
        """Test that pip creates pyproject.toml with dev dependencies."""
        _migrate_requirements_to_pyproject(python_pip_project)
        pm = PackageManager.PIP
        deps = ["pytest"]
        pm.add(deps)
        assert_deps_updated(deps, pm)

    def test_add_with_pip_failure(self, python_pip_project: Path) -> None:
        """Test package installation failure with poetry."""
        _migrate_requirements_to_pyproject(python_pip_project)
        pm = PackageManager.PIP
        with pytest.raises(RuntimeError, match="Failed to install dev dependencies"):
            pm.add(["non-existent-package-12345"])
