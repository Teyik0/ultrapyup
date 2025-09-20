from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import toml

from ultrapyup.config.ruff import (
    RuffConfigError,
    _find_site_packages_path,
    _get_base_config_path,
    _has_existing_ruff_config,
    _load_pyproject_toml,
    _save_pyproject_toml,
    _update_ruff_config,
    ruff_config_setup,
)


class TestLoadPyprojectToml:
    """Test suite for pyproject.toml loading functionality."""

    def test_load_pyproject_toml_success(self, project_dir: Path) -> None:
        """Test successful loading of pyproject.toml."""
        # Arrange
        pyproject_content = """
[project]
name = "test-project"
version = "0.1.0"
"""
        pyproject_path = project_dir / "pyproject.toml"
        pyproject_path.write_text(pyproject_content)

        # Act
        config = _load_pyproject_toml(pyproject_path)

        # Assert
        assert config["project"]["name"] == "test-project"
        assert config["project"]["version"] == "0.1.0"

    def test_load_pyproject_toml_file_not_found(self, project_dir: Path) -> None:
        """Test error handling when pyproject.toml doesn't exist."""
        # Arrange
        pyproject_path = project_dir / "nonexistent.toml"

        # Act & Assert
        with pytest.raises(RuffConfigError, match=r"Could not read pyproject\.toml"):
            _load_pyproject_toml(pyproject_path)

    def test_load_pyproject_toml_invalid_content(self, project_dir: Path) -> None:
        """Test error handling with invalid TOML content."""
        # Arrange
        pyproject_path = project_dir / "pyproject.toml"
        pyproject_path.write_text("invalid toml content [[[")

        # Act & Assert
        with pytest.raises(RuffConfigError, match=r"Could not read pyproject\.toml"):
            _load_pyproject_toml(pyproject_path)


class TestSavePyprojectToml:
    """Test suite for pyproject.toml saving functionality."""

    def test_save_pyproject_toml_success(self, project_dir: Path) -> None:
        """Test successful saving of pyproject.toml."""
        # Arrange
        pyproject_path = project_dir / "pyproject.toml"
        config = {"project": {"name": "test-project", "version": "0.1.0"}}

        # Act
        _save_pyproject_toml(pyproject_path, config)

        # Assert
        with open(pyproject_path) as f:
            saved_config = toml.load(f)
        assert saved_config["project"]["name"] == "test-project"
        assert saved_config["project"]["version"] == "0.1.0"

    def test_save_pyproject_toml_permission_error(self, project_dir: Path) -> None:
        """Test error handling when file cannot be written."""
        # Arrange
        pyproject_path = project_dir / "readonly.toml"
        config = {"project": {"name": "test"}}

        # Create readonly file
        pyproject_path.touch()
        pyproject_path.chmod(0o444)

        # Act & Assert
        with pytest.raises(RuffConfigError, match=r"Could not write pyproject\.toml"):
            _save_pyproject_toml(pyproject_path, config)


class TestFindSitePackagesPath:
    """Test suite for site-packages path detection."""

    def test_find_site_packages_linux_path(self, project_dir: Path) -> None:
        """Test finding site-packages in Linux/macOS .venv structure."""
        # Arrange
        venv_path = project_dir / ".venv/lib/python3.11/site-packages"
        venv_path.mkdir(parents=True)

        # Act
        result = _find_site_packages_path()

        # Assert
        assert result is not None
        assert result.name == "site-packages"
        assert result.exists()
        assert str(result).endswith(".venv/lib/python3.11/site-packages")

    def test_find_site_packages_windows_path(self, project_dir: Path) -> None:
        """Test finding site-packages in Windows .venv structure."""
        # Arrange
        venv_path = project_dir / ".venv/Lib/site-packages"
        venv_path.mkdir(parents=True)

        # Act
        result = _find_site_packages_path()

        # Assert
        assert result is not None
        assert result.name == "site-packages"
        assert result.exists()
        assert str(result).endswith(".venv/Lib/site-packages")

    def test_find_site_packages_lib64_path(self, project_dir: Path) -> None:
        """Test finding site-packages in lib64 directory."""
        # Arrange
        venv_path = project_dir / ".venv/lib64/python3.11/site-packages"
        venv_path.mkdir(parents=True)

        # Act
        result = _find_site_packages_path()

        # Assert
        assert result is not None
        assert result.name == "site-packages"
        assert str(result).endswith(".venv/lib64/python3.11/site-packages")

    def test_find_site_packages_multiple_python_versions(self, project_dir: Path) -> None:
        """Test finding site-packages when multiple Python versions exist."""
        # Arrange
        # Create multiple Python version directories
        python39_path = project_dir / ".venv/lib/python3.9/site-packages"
        python311_path = project_dir / ".venv/lib/python3.11/site-packages"
        python39_path.mkdir(parents=True)
        python311_path.mkdir(parents=True)

        # Act
        result = _find_site_packages_path()

        # Assert - should find one of them
        assert result is not None
        assert result.name == "site-packages"
        assert result.exists()
        assert str(result).endswith("site-packages")

    def test_find_site_packages_not_found(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test when no site-packages directory is found."""
        # Arrange - no .venv directory in project_dir

        # Act
        result = _find_site_packages_path()

        # Assert
        assert result is None

    def test_find_site_packages_empty_venv(self, project_dir: Path) -> None:
        """Test when .venv exists but has no python directories."""
        # Arrange
        venv_lib_path = project_dir / ".venv/lib"
        venv_lib_path.mkdir(parents=True)

        # Act
        result = _find_site_packages_path()

        # Assert
        assert result is None


class TestGetBaseConfigPath:
    """Test suite for base configuration path retrieval."""

    def test_get_base_config_path_success(self, project_dir: Path) -> None:
        """Test successful retrieval of base config path."""
        # Arrange
        site_packages = project_dir / ".venv/lib/python3.11/site-packages"
        site_packages.mkdir(parents=True)

        # Act
        result = _get_base_config_path()

        # Assert
        assert result.endswith("ultrapyup/resources/ruff_base.toml")
        assert ".venv/lib/python3.11/site-packages" in result

    def test_get_base_config_path_no_site_packages(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test error when site-packages directory is not found."""
        # Arrange - no .venv directory in project_dir

        # Act & Assert
        with pytest.raises(RuffConfigError, match="No virtualenv site-packages directory found"):
            _get_base_config_path()


class TestHasExistingRuffConfig:
    """Test suite for existing Ruff configuration detection."""

    def test_has_existing_ruff_config_true(self) -> None:
        """Test detection when Ruff config exists."""
        # Arrange
        config = {"tool": {"ruff": {"line-length": 88}}}

        # Act
        result = _has_existing_ruff_config(config)

        # Assert
        assert result is True

    def test_has_existing_ruff_config_false_no_tool(self) -> None:
        """Test detection when no tool section exists."""
        # Arrange
        config = {"project": {"name": "test"}}

        # Act
        result = _has_existing_ruff_config(config)

        # Assert
        assert result is False

    def test_has_existing_ruff_config_false_no_ruff(self) -> None:
        """Test detection when tool section exists but no ruff config."""
        # Arrange
        config = {"tool": {"pytest": {"python_files": "test_*.py"}}}

        # Act
        result = _has_existing_ruff_config(config)

        # Assert
        assert result is False


class TestUpdateRuffConfig:
    """Test suite for Ruff configuration updates."""

    def test_update_ruff_config_new_tool_section(self) -> None:
        """Test updating config when no tool section exists."""
        # Arrange
        config = {"project": {"name": "test"}}
        base_config_path = "/path/to/ruff_base.toml"

        # Act
        _update_ruff_config(config, base_config_path)

        # Assert
        assert "tool" in config
        assert "ruff" in config["tool"]
        assert config["tool"]["ruff"]["extend"] == base_config_path

    def test_update_ruff_config_existing_tool_section(self) -> None:
        """Test updating config when tool section already exists."""
        # Arrange
        config = {"tool": {"pytest": {"python_files": "test_*.py"}}}
        base_config_path = "/path/to/ruff_base.toml"

        # Act
        _update_ruff_config(config, base_config_path)

        # Assert
        assert config["tool"]["pytest"]["python_files"] == "test_*.py"  # Preserved
        assert config["tool"]["ruff"]["extend"] == base_config_path

    def test_update_ruff_config_override_existing_ruff(self) -> None:
        """Test updating config when Ruff config already exists."""
        # Arrange
        config = {"tool": {"ruff": {"line-length": 120}}}
        base_config_path = "/path/to/ruff_base.toml"

        # Act
        _update_ruff_config(config, base_config_path)

        # Assert
        assert config["tool"]["ruff"]["extend"] == base_config_path
        # Should override existing config
        assert "line-length" not in config["tool"]["ruff"]


class TestRuffConfigSetup:
    """Test suite for main ruff configuration setup function."""

    @patch("ultrapyup.config.ruff.log")
    def test_ruff_config_setup_no_pyproject_toml(self, mock_log: Mock, project_dir: Path) -> None:  # noqa: ARG002
        """Test setup when no pyproject.toml exists."""
        # Arrange - no pyproject.toml file in project_dir

        # Act
        ruff_config_setup()

        # Assert
        mock_log.info.assert_called_with("No pyproject.toml found, skipping Ruff configuration")

    @patch("ultrapyup.config.ruff.log")
    def test_ruff_config_setup_success_new_config(self, mock_log: Mock, project_with_ruff_config: Path) -> None:
        """Test successful setup with new Ruff configuration."""
        # Arrange
        pyproject_path = project_with_ruff_config / "pyproject.toml"

        # Remove existing ruff config to test new config scenario
        with open(pyproject_path) as f:
            config = toml.load(f)

        # Remove ruff config but keep the rest
        if "tool" in config and "ruff" in config["tool"]:
            del config["tool"]["ruff"]

        with open(pyproject_path, "w") as f:
            toml.dump(config, f)

        # Act
        ruff_config_setup()

        # Assert
        mock_log.title.assert_called_with("Ruff configuration setup completed")
        mock_log.info.assert_called()

        # Verify config was updated
        with open(pyproject_path) as f:
            updated_config = toml.load(f)

        assert "tool" in updated_config
        assert "ruff" in updated_config["tool"]
        assert "extend" in updated_config["tool"]["ruff"]

    @patch("ultrapyup.config.ruff.log")
    def test_ruff_config_setup_success_override_config(self, mock_log: Mock, project_with_ruff_config: Path) -> None:  # noqa: ARG002
        """Test successful setup when overriding existing Ruff configuration."""
        # Arrange - project_with_ruff_config already has ruff config

        # Act
        ruff_config_setup()

        # Assert
        mock_log.title.assert_called_with("Ruff configuration setup completed")

        # Verify "Override" message was logged
        call_args = [call.args[0] for call in mock_log.info.call_args_list]
        override_messages = [msg for msg in call_args if msg.startswith("Override")]
        assert len(override_messages) > 0

    @patch("ultrapyup.config.ruff.log")
    def test_ruff_config_setup_invalid_toml(self, mock_log: Mock, project_dir: Path) -> None:
        """Test setup with invalid TOML content."""
        # Arrange
        pyproject_path = project_dir / "pyproject.toml"
        pyproject_path.write_text("invalid toml [[[")

        # Act
        ruff_config_setup()

        # Assert
        mock_log.info.assert_called()
        call_args = mock_log.info.call_args[0][0]
        assert "Could not read pyproject.toml" in call_args

    @patch("ultrapyup.config.ruff.log")
    def test_ruff_config_setup_no_venv(self, mock_log: Mock, project_dir: Path) -> None:
        """Test setup when no virtual environment is found."""
        # Arrange
        pyproject_content = """
[project]
name = "test-project"
version = "0.1.0"
"""
        (project_dir / "pyproject.toml").write_text(pyproject_content)
        # No .venv directory

        # Act
        ruff_config_setup()

        # Assert
        mock_log.info.assert_called()
        call_args = mock_log.info.call_args[0][0]
        assert "No virtualenv site-packages directory found" in call_args

    @patch("ultrapyup.config.ruff.log")
    @patch("ultrapyup.config.ruff._save_pyproject_toml")
    def test_ruff_config_setup_save_error(
        self,
        mock_save: Mock,
        mock_log: Mock,
        project_with_ruff_config: Path,  # noqa: ARG002
    ) -> None:
        """Test setup when saving fails."""
        # Arrange
        mock_save.side_effect = RuffConfigError("Permission denied")

        # Act
        ruff_config_setup()

        # Assert
        mock_log.info.assert_called_with("Permission denied")

    @patch("ultrapyup.config.ruff.log")
    @patch("ultrapyup.config.ruff._load_pyproject_toml")
    def test_ruff_config_setup_unexpected_error(self, mock_load: Mock, mock_log: Mock, project_dir: Path) -> None:
        """Test setup with unexpected error."""
        # Arrange
        (project_dir / "pyproject.toml").touch()
        mock_load.side_effect = ValueError("Unexpected error")

        # Act
        ruff_config_setup()

        # Assert
        mock_log.info.assert_called()
        call_args = mock_log.info.call_args[0][0]
        assert "Unexpected error during Ruff configuration" in call_args


class TestRuffConfigError:
    """Test suite for RuffConfigError exception."""

    def test_ruff_config_error_creation(self) -> None:
        """Test RuffConfigError can be created and raised."""
        # Arrange
        message = "Test error message"

        # Act & Assert
        with pytest.raises(RuffConfigError, match="Test error message"):
            raise RuffConfigError(message)

    def test_ruff_config_error_with_cause(self) -> None:
        """Test RuffConfigError with underlying cause."""
        # Arrange
        original_error = FileNotFoundError("File not found")

        # Act & Assert
        with pytest.raises(RuffConfigError) as exc_info:
            raise RuffConfigError("Wrapper error") from original_error

        assert exc_info.value.__cause__ == original_error
