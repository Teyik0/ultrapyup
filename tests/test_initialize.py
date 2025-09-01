"""Tests for the initialize module."""

from pathlib import Path
from unittest.mock import patch

from ultrapy.initialize import (
    _check_python_project,
    _migrate_requirements_to_pyproject,
    initialize,
)


class TestCheckPythonProject:
    """Tests for _check_python_project function."""

    def test_no_python_project(self, project_dir: Path, capsys):
        """Test when no Python project files exist."""
        result = _check_python_project()

        assert result is False
        captured = capsys.readouterr()
        assert "No Python project detected" in captured.out

    def test_with_venv_only(self, project_dir: Path):
        """Test when only .venv directory exists."""
        venv_path = project_dir / ".venv"
        venv_path.mkdir()

        result = _check_python_project()

        assert result is True

    def test_with_requirements_txt(self, project_with_requirements: Path):
        """Test when requirements.txt exists."""
        result = _check_python_project()

        assert result is True

        pyproject_path = project_with_requirements / "pyproject.toml"
        assert pyproject_path.exists()

        content = pyproject_path.read_text()
        assert "requests==2.31.0" in content
        assert "pytest>=7.0.0" in content
        assert "black==23.0.0" in content
        assert "ruff>=0.1.0" in content

    def test_with_pyproject_toml(self, python_uv_project: Path):
        """Test when pyproject.toml exists."""
        result = _check_python_project()

        assert result is True


class TestMigrateRequirementsToPyproject:
    """Tests for _migrate_requirements_to_pyproject function."""

    def test_successful_migration(self, project_dir: Path, capsys):
        """Test successful migration from requirements.txt to pyproject.toml."""
        requirements_content = """requests==2.31.0
pytest>=7.0.0
black==23.0.0"""
        (project_dir / "requirements.txt").write_text(requirements_content)

        _migrate_requirements_to_pyproject()

        pyproject_path = project_dir / "pyproject.toml"
        assert pyproject_path.exists()

        content = pyproject_path.read_text()
        assert '"requests==2.31.0"' in content
        assert '"pytest>=7.0.0"' in content
        assert '"black==23.0.0"' in content
        assert "[build-system]" in content
        assert "uv_build" in content

        captured = capsys.readouterr()
        assert "Migrated requirements.txt to pyproject.toml" in captured.out
        assert "Found 3 dependencies" in captured.out

    def test_no_migration_when_pyproject_exists(self, project_dir: Path):
        """Test that migration doesn't happen when pyproject.toml already exists."""
        (project_dir / "requirements.txt").write_text("requests==2.31.0\n")

        existing_content = "[project]\nname = 'existing'\n"
        (project_dir / "pyproject.toml").write_text(existing_content)

        _migrate_requirements_to_pyproject()

        # Content should remain unchanged
        content = (project_dir / "pyproject.toml").read_text()
        assert content == existing_content
        assert "requests" not in content

    def test_no_migration_when_no_requirements(self, project_dir: Path):
        """Test that migration doesn't happen when requirements.txt doesn't exist."""
        _migrate_requirements_to_pyproject()

        pyproject_path = project_dir / "pyproject.toml"
        assert not pyproject_path.exists()

    def test_migration_handles_comments_and_empty_lines(self, project_dir: Path):
        """Test that migration correctly handles comments and empty lines."""
        requirements_content = """# Main dependencies
requests==2.31.0

# Testing tools
pytest>=7.0.0
# This is a comment

black==23.0.0

"""
        (project_dir / "requirements.txt").write_text(requirements_content)

        _migrate_requirements_to_pyproject()

        pyproject_path = project_dir / "pyproject.toml"
        content = pyproject_path.read_text()

        # Should have only the actual dependencies
        assert '"requests==2.31.0"' in content
        assert '"pytest>=7.0.0"' in content
        assert '"black==23.0.0"' in content
        assert "# Main dependencies" not in content
        assert "# Testing tools" not in content
        assert "# This is a comment" not in content

    def test_migration_handles_read_error(self, project_dir: Path):
        """Test handling of read errors during migration."""
        requirements_path = project_dir / "requirements.txt"

        requirements_path.write_bytes(b"\xff\xfe")  # Invalid UTF-8

        import pytest

        with pytest.raises(UnicodeDecodeError):
            _migrate_requirements_to_pyproject()

        pyproject_path = project_dir / "pyproject.toml"
        assert not pyproject_path.exists()


class TestInitialize:
    """Tests for the main initialize function."""

    def test_initialize_exits_early_without_project(self, project_dir: Path):
        """Test that initialize exits early when no Python project exists."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            # Mock get_package_manager inquire call
            mock_inquirer.return_value.execute.return_value = "uv"
            result = initialize()

            # Should not call inquirer if no project exists
            mock_inquirer.assert_not_called()
            assert result is None

    def test_initialize_with_minimal_project(self, python_empty_project: Path, capsys):
        """Test initialize with a minimal Python project."""
        # Create pyproject.toml to avoid migration
        (python_empty_project / "pyproject.toml").write_text(
            "[project]\nname = 'test'\nversion = '0.1.0'\nrequires-python = '>=3.8'"
        )

        # Only mock inquirer to control user choices
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            # Set up inquirer mock to return choices for package manager, editors, and precommit
            mock_inquirer.return_value.execute.side_effect = ["uv", [], []]

            result = initialize()
            captured = capsys.readouterr()
            assert "uv" in captured.out  # Package manager selection logged
            assert "Dependencies installed" in captured.out  # From install_dependencies
            assert "ruff, ty, ultrapy" in captured.out  # Dependencies list
            assert (
                "Ruff configuration setup completed" in captured.out
            )  # From ruff_config_setup
            assert result is None

    def test_initialize_with_precommit_tools(self, python_uv_project: Path, capsys):
        """Test initialize with pre-commit tools selected."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            # Set up inquirer mock to return choices: no editors, lefthook precommit
            mock_inquirer.return_value.execute.side_effect = [[], ["Lefthook"]]

            result = initialize()
            captured = capsys.readouterr()
            assert "uv" in captured.out  # Package manager auto-detected
            assert "Dependencies installed" in captured.out  # From install_dependencies
            assert "lefthook" in captured.out  # Precommit tool in dependencies and logs
            assert (
                "Ruff configuration setup completed" in captured.out
            )  # From ruff_config_setup
            assert "Pre-commit setup completed" in captured.out  # From precommit setup
            assert "lefthook.yaml created" in captured.out  # Precommit file created
            assert result is None

    def test_initialize_with_editors(self, python_uv_project: Path, capsys):
        """Test initialize with editors selected."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            # Set up inquirer mock to return choices: Zed editor, no precommit
            mock_inquirer.return_value.execute.side_effect = [["Zed"], []]

            result = initialize()
            captured = capsys.readouterr()
            assert "uv" in captured.out  # Package manager auto-detected
            assert "Dependencies installed" in captured.out  # From install_dependencies
            assert (
                "Ruff configuration setup completed" in captured.out
            )  # From ruff_config_setup
            assert "Editor setup completed" in captured.out  # From editor setup
            assert ".rules, .zed created" in captured.out  # Editor files created
            assert result is None

    def test_initialize_full_flow(self, project_with_requirements: Path, capsys):
        """Test complete initialization flow with all options."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            # Set up inquirer mock to return choices: pip (auto-detected), Zed editor, Lefthook precommit
            mock_inquirer.return_value.execute.side_effect = [
                ["Zed"],
                ["Lefthook"],
            ]

            result = initialize()
            assert (project_with_requirements / "pyproject.toml").exists()

            captured = capsys.readouterr()
            assert "Migrated requirements.txt to pyproject.toml" in captured.out
            assert "Found 4 dependencies" in captured.out  # From migration (
            assert "pip" in captured.out  # Package manager selection logged
            assert "Dependencies installed" in captured.out  # From install_dependencies
            assert "lefthook" in captured.out  # Precommit tool in dependencies
            assert (
                "Ruff configuration setup completed" in captured.out
            )  # From ruff_config_setup
            assert "Pre-commit setup completed" in captured.out  # From precommit setup
            assert "lefthook.yaml created" in captured.out  # Precommit file created
            assert "Editor setup completed" in captured.out  # From editor setup
            assert ".rules, .zed created" in captured.out  # Editor files created
            assert result is None
