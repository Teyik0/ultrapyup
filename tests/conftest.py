import shutil
import subprocess
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def project_dir(temp_dir: Path) -> Generator[Path, None, None]:
    """Create a temporary project directory and change to it."""
    original_dir = Path.cwd()
    try:
        # Change to temp directory
        import os

        os.chdir(temp_dir)
        yield temp_dir
    finally:
        # Restore original directory
        os.chdir(original_dir)


@pytest.fixture
def python_uv_project(project_dir: Path) -> Path:
    """Create a basic Python project with uv init."""
    subprocess.run(
        ["uv", "init", "--name", "test-project", "--lib"],
        cwd=project_dir,
        capture_output=True,
        check=False,
    )

    subprocess.run(
        ["uv", "sync"],
        cwd=project_dir,
        capture_output=True,
        check=False,
    )

    return project_dir


@pytest.fixture
def python_empty_project(project_dir: Path) -> Path:
    """Create a Python project with just a .venv directory."""
    subprocess.run(
        ["python", "-m", "venv", ".venv"],
        cwd=project_dir,
        capture_output=True,
        check=True,
    )

    return project_dir


@pytest.fixture
def project_with_requirements(python_empty_project: Path) -> Path:
    """Create a project with requirements.txt."""
    requirements_content = """# Test requirements
requests==2.31.0
pytest>=7.0.0
# Comment line
black==23.0.0

# Empty lines above and below

ruff>=0.1.0
"""
    (python_empty_project / "requirements.txt").write_text(requirements_content)

    return python_empty_project


@pytest.fixture
def project_with_ruff_config(project_with_pyproject: Path) -> Path:
    """Create a project with existing Ruff configuration in pyproject.toml."""
    pyproject_path = project_with_pyproject / "pyproject.toml"
    pyproject_content = pyproject_path.read_text()

    # Add [tool.ruff] and [tool.ruff.lint] sections to the end
    ruff_config = """
[tool.ruff]
line-length = 120
target-version = "py39"

[tool.ruff.lint]
select = ["E", "F"]
ignore = ["E501"]
"""
    pyproject_path.write_text(pyproject_content + "\n" + ruff_config)

    # Create .venv with proper structure
    venv_path = project_with_pyproject / ".venv"
    lib_path = venv_path / "lib" / "python3.11"
    site_packages = lib_path / "site-packages"
    site_packages.mkdir(parents=True)

    # Create ultrapy package structure in site-packages
    ultrapy_path = site_packages / "ultrapy"
    resources_path = ultrapy_path / "resources"
    resources_path.mkdir(parents=True)

    # Create ruff_base.toml
    ruff_base_content = """# Ultrapy base Ruff configuration
line-length = 88
target-version = "py310"

[lint]
select = ["E", "F", "I"]
"""
    (resources_path / "ruff_base.toml").write_text(ruff_base_content)

    return project_with_pyproject


@pytest.fixture
def mock_console():
    """Create a mock console for testing output."""
    from ultrapy.utils import console

    return console


@pytest.fixture
def mock_log():
    """Create a mock log for testing output."""
    from ultrapy.utils import log

    return log
