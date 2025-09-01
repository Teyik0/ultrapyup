from pathlib import Path
from unittest.mock import patch

from ultrapy.initialize import _migrate_requirements_to_pyproject
from ultrapy.package_manager import (
    PackageManager,
    get_package_manager,
    install_dependencies,
    ruff_config_setup,
)
from ultrapy.pre_commit import options as pre_commit_options


class TestGetPackageManager:
    """Tests for get_package_manager function."""

    def test_auto_detect_uv_lock(self, python_uv_project: Path, capsys):
        """Test auto-detection when uv.lock exists."""

        result = get_package_manager()

        assert isinstance(result, PackageManager)
        assert result.name == "uv"
        assert result.add_cmd == "uv add"
        assert result.lockfile == "uv.lock"

        captured = capsys.readouterr()
        assert "Package manager auto detected" in captured.out
        assert "uv" in captured.out

    def test_auto_detect_requirements_txt(
        self, project_with_requirements: Path, capsys
    ):
        """Test auto-detection when requirements.txt exists."""
        result = get_package_manager()

        assert isinstance(result, PackageManager)
        assert result.name == "pip"
        assert result.add_cmd == "pip install"
        assert result.lockfile == "requirements.txt"

        captured = capsys.readouterr()
        assert "Package manager auto detected" in captured.out
        assert "pip" in captured.out

    def test_manual_selection_when_no_lockfile(self, python_empty_project: Path):
        """Test manual selection when no lockfile exists."""
        with patch("ultrapy.package_manager.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = "uv"
            result = get_package_manager()

            assert result.name == "uv"
            assert result.add_cmd == "uv add"
            assert result.lockfile == "uv.lock"

    def test_manual_selection_pip(self, python_empty_project: Path):
        """Test manual selection of pip."""
        with patch("ultrapy.package_manager.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = "pip"
            result = get_package_manager()

            assert result.name == "pip"
            assert result.add_cmd == "pip install"
            assert result.lockfile == "requirements.txt"

    def test_invalid_selection_raises_error(self, project_dir: Path):
        """Test that invalid selection raises ValueError."""
        with patch("ultrapy.package_manager.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = "invalid_manager"

            import pytest

            with pytest.raises(
                ValueError, match="Unknown package manager: invalid_manager"
            ):
                get_package_manager()


class TestInstallDependencies:
    """Tests for install_dependencies function."""

    def test_install_with_uv_no_precommit(self, python_uv_project: Path, capsys):
        """Test installing dependencies with uv and no pre-commit tools."""
        pm = PackageManager("uv", "uv add", "uv.lock")
        install_dependencies(pm, None)

        captured = capsys.readouterr()
        assert "Dependencies installed" in captured.out
        assert "ruff, ty, ultrapy" in captured.out

        pyproject_path = python_uv_project / "pyproject.toml"
        pyproject = pyproject_path.read_text()
        assert "ruff" in pyproject
        assert "ty" in pyproject

    def test_install_with_uv_and_precommit(self, python_uv_project: Path, capsys):
        """Test installing dependencies with uv and pre-commit tools."""
        pm = PackageManager("uv", "uv add", "uv.lock")
        install_dependencies(pm, [pre_commit_options[0]])

        captured = capsys.readouterr()
        assert "Dependencies installed" in captured.out
        assert "ruff, ty, ultrapy, lefthook" in captured.out

        pyproject_path = python_uv_project / "pyproject.toml"
        pyproject = pyproject_path.read_text()
        assert "ruff" in pyproject
        assert "ty" in pyproject
        assert "lefthook" in pyproject

    def test_install_with_pip_no_precommit(
        self, project_with_requirements: Path, capsys
    ):
        """Test installing dependencies with pip and no pre-commit tools."""
        pm = PackageManager("pip", "pip install", "requirements.txt")
        _migrate_requirements_to_pyproject()
        install_dependencies(pm, None)

        captured = capsys.readouterr()
        assert "Dependencies installed" in captured.out
        assert "ruff, ty, ultrapy" in captured.out

        pyproject_path = project_with_requirements / "pyproject.toml"
        pyproject = pyproject_path.read_text()

        assert "ruff" in pyproject
        assert "ty" in pyproject
        assert "requests" in pyproject
        assert "pytest" in pyproject
        assert "black" in pyproject

    def test_install_with_pip_and_precommit(
        self, project_with_requirements: Path, capsys
    ):
        """Test installing dependencies with pip and pre-commit tools."""
        pm = PackageManager("pip", "pip install", "requirements.txt")
        _migrate_requirements_to_pyproject()
        install_dependencies(pm, [pre_commit_options[0]])

        captured = capsys.readouterr()
        assert "Dependencies installed" in captured.out
        assert "ruff, ty, ultrapy, lefthook" in captured.out

        pyproject_path = project_with_requirements / "pyproject.toml"
        pyproject = pyproject_path.read_text()

        assert "ruff" in pyproject
        assert "ty" in pyproject
        assert "lefthook" in pyproject
        assert "requests" in pyproject
        assert "pytest" in pyproject
        assert "black" in pyproject


class TestRuffConfigSetup:
    """Tests for ruff_config_setup function."""

    def test_no_pyproject_toml(self, project_dir: Path, capsys):
        """Test when pyproject.toml doesn't exist."""
        ruff_config_setup()

        captured = capsys.readouterr()
        assert "No pyproject.toml found" in captured.out

    def test_invalid_pyproject_toml(self, project_dir: Path, capsys):
        """Test when pyproject.toml is invalid."""
        (project_dir / "pyproject.toml").write_text("invalid toml content {]")

        ruff_config_setup()

        captured = capsys.readouterr()
        assert "Could not read pyproject.toml" in captured.out

    def test_add_ruff_config_to_new_pyproject(self, python_uv_project: Path, capsys):
        """Test adding Ruff config to pyproject.toml without existing Ruff config."""
        ruff_config_setup()

        import toml

        updated_toml = toml.load(python_uv_project / "pyproject.toml")
        assert "tool" in updated_toml
        assert "ruff" in updated_toml["tool"]
        assert (
            "site-packages/ultrapy/resources/ruff_base.toml"
            in updated_toml["tool"]["ruff"]["extend"]
        )

        # Original content should still be there
        assert updated_toml["project"]["name"] == "test-project"

        captured = capsys.readouterr()
        assert "Added Ruff config in pyproject.toml" in captured.out

    def test_override_existing_ruff_config(self, python_uv_project: Path, capsys):
        """Test overriding existing Ruff configuration."""
        import toml

        with open(python_uv_project / "pyproject.toml") as f:
            pyproject = toml.load(f)

            pyproject["tool"] = pyproject.get("tool", {})
            pyproject["tool"]["ruff"] = {
                "line-length": 120,
                "target-version": "py39",
            }
            pyproject["tool"]["ruff.lint"] = {"select": ["E", "F"]}
            pyproject["tool"]["other"] = {"key": "value"}

        with open(python_uv_project / "pyproject.toml", "w") as f:
            toml.dump(pyproject, f)

        ruff_config_setup()

        # Check the updated content
        updated_toml = toml.load(python_uv_project / "pyproject.toml")

        # New ruff config should be there
        assert "tool" in updated_toml
        assert "ruff" in updated_toml["tool"]
        assert (
            "site-packages/ultrapy/resources/ruff_base.toml"
            in updated_toml["tool"]["ruff"]["extend"]
        )

        # Other sections should remain
        assert "other" in updated_toml["tool"]
        assert updated_toml["tool"]["other"]["key"] == "value"

        captured = capsys.readouterr()
        assert "Override Ruff config in pyproject.toml" in captured.out

    def test_no_venv_lib_directory(self, project_dir: Path, capsys):
        """Test when .venv/lib directory doesn't exist."""
        (project_dir / "pyproject.toml").write_text("[project]\nname = 'test'\n")

        ruff_config_setup()

        captured = capsys.readouterr()
        assert "No .venv/lib directory found" in captured.out

    def test_no_python_version_in_venv(self, project_dir: Path, capsys):
        """Test when no python* directory exists in .venv/lib."""
        (project_dir / "pyproject.toml").write_text("[project]\nname = 'test'\n")

        # Create .venv/lib without python* directory
        venv_lib = project_dir / ".venv" / "lib"
        venv_lib.mkdir(parents=True)

        ruff_config_setup()

        captured = capsys.readouterr()
        assert "No Python version directory found in .venv/lib" in captured.out
