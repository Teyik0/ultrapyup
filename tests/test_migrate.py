from pathlib import Path

import pytest

from ultrapyup.migrate import _check_python_project, _migrate_requirements_to_pyproject


class TestCheckPythonProject:
    """Tests for _check_python_project function."""

    def test_no_python_project(self, project_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:  # noqa: ARG002
        """Test when no Python project files exist."""
        result = _check_python_project()

        assert result is False
        captured = capsys.readouterr()
        assert "No Python project detected" in captured.out

    def test_with_venv_only(self, project_dir: Path) -> None:
        """Test when only .venv directory exists."""
        venv_path = project_dir / ".venv"
        venv_path.mkdir()

        result = _check_python_project()

        assert result is True

    def test_with_requirements_txt(self, project_with_requirements: Path) -> None:
        """Test when requirements.txt exists."""
        result = _check_python_project()

        assert result is True

        requirements_txt = project_with_requirements / "requirements.txt"
        assert requirements_txt.exists()

        content = requirements_txt.read_text()
        assert "requests==2.31.0" in content
        assert "pytest>=7.0.0" in content
        assert "tqdm>=4.67.1" in content
        assert "ruff>=0.1.0" in content

    def test_with_pyproject_toml(self, python_uv_project: Path) -> None:  # noqa: ARG002
        """Test when pyproject.toml exists."""
        result = _check_python_project()

        assert result is True


class TestMigrateRequirementsToPyproject:
    """Tests for _migrate_requirements_to_pyproject function."""

    def test_successful_migration(self, project_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Test successful migration from requirements.txt to pyproject.toml."""
        requirements_content = """requests==2.31.0
pytest>=7.0.0
black==23.0.0"""
        (project_dir / "requirements.txt").write_text(requirements_content)

        _migrate_requirements_to_pyproject()

        pyproject_path = project_dir / "pyproject.toml"
        assert pyproject_path.exists()

        content = pyproject_path.read_text()
        assert "requests==2.31.0" in content
        assert "pytest>=7.0.0" in content
        assert "black==23.0.0" in content

        captured = capsys.readouterr()
        assert "Migrated requirements.txt to pyproject.toml" in captured.out
        assert "Found 3 dependencies" in captured.out

    def test_no_migration_when_pyproject_exists(self, project_dir: Path) -> None:
        """Test that migration doesn't happen when pyproject.toml already exists."""
        (project_dir / "requirements.txt").write_text("requests==2.31.0\n")

        existing_content = "[project]\nname = 'existing'\n"
        (project_dir / "pyproject.toml").write_text(existing_content)

        _migrate_requirements_to_pyproject()

        # Content should remain unchanged
        content = (project_dir / "pyproject.toml").read_text()
        assert content == existing_content
        assert "requests" not in content

    def test_no_migration_when_no_requirements(self, project_dir: Path) -> None:
        """Test that migration doesn't happen when requirements.txt doesn't exist."""
        _migrate_requirements_to_pyproject()

        pyproject_path = project_dir / "pyproject.toml"
        assert not pyproject_path.exists()

    def test_migration_handles_comments_and_empty_lines(self, project_dir: Path) -> None:
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

    def test_migration_handles_read_error(self, project_dir: Path) -> None:
        """Test handling of read errors during migration."""
        requirements_path = project_dir / "requirements.txt"

        requirements_path.write_bytes(b"\xff\xfe")  # Invalid UTF-8

        with pytest.raises(UnicodeDecodeError):
            _migrate_requirements_to_pyproject()

        pyproject_path = project_dir / "pyproject.toml"
        assert not pyproject_path.exists()
