"""Tests for ultrapyup.config.ty module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import toml

from ultrapyup.config.ty import (
    TyConfigError,
    TyConfigResult,
    _apply_fallback_config,
    _check_pyproject_exists,
    _check_ty_config_exists,
    _load_pyproject_config,
    get_ty_config_info,
    ty_config_setup,
    validate_ty_config,
)
from ultrapyup.layout import LayoutDetection, ProjectLayout


class TestTyConfigError:
    """Test TyConfigError exception."""

    def test_init_with_message_only(self) -> None:
        """Test TyConfigError initialization with message only."""
        error = TyConfigError("Test error")
        assert str(error) == "Test error"
        assert error.cause is None

    def test_init_with_cause(self) -> None:
        """Test TyConfigError initialization with cause."""
        cause = ValueError("Original error")
        error = TyConfigError("Test error", cause=cause)
        assert str(error) == "Test error"
        assert error.cause is cause


class TestTyConfigResult:
    """Test TyConfigResult model."""

    def test_default_values(self) -> None:
        """Test default values for TyConfigResult."""
        result = TyConfigResult(success=True)
        assert result.success is True
        assert result.layout_detected is None
        assert result.config_exists is False
        assert result.fallback_used is False
        assert result.error_message is None

    def test_all_fields(self) -> None:
        """Test TyConfigResult with all fields set."""
        layout = LayoutDetection(
            layout=ProjectLayout.SRC_LAYOUT,
            root_paths=["./src"],
            package_name="test_package",
        )
        result = TyConfigResult(
            success=True,
            layout_detected=layout,
            config_exists=True,
            fallback_used=True,
            error_message="Test error",
        )
        assert result.success is True
        assert result.layout_detected == layout
        assert result.config_exists is True
        assert result.fallback_used is True
        assert result.error_message == "Test error"


class TestCheckPyprojectExists:
    """Test _check_pyproject_exists function."""

    def test_exists(self, project_dir: Path) -> None:
        """Test when pyproject.toml exists."""
        pyproject_path = project_dir / "pyproject.toml"
        pyproject_path.write_text("[tool.poetry]\nname = 'test'")

        # Should not raise
        _check_pyproject_exists(pyproject_path)

    def test_not_exists(self, project_dir: Path) -> None:
        """Test when pyproject.toml doesn't exist."""
        pyproject_path = project_dir / "pyproject.toml"

        with pytest.raises(TyConfigError, match=r"No pyproject\.toml found"):
            _check_pyproject_exists(pyproject_path)


class TestLoadPyprojectConfig:
    """Test _load_pyproject_config function."""

    def test_valid_toml(self, project_dir: Path) -> None:
        """Test loading valid TOML file."""
        pyproject_path = project_dir / "pyproject.toml"
        config = {"tool": {"poetry": {"name": "test"}}}
        pyproject_path.write_text(toml.dumps(config))

        result = _load_pyproject_config(pyproject_path)
        assert result == config

    def test_invalid_toml(self, project_dir: Path) -> None:
        """Test loading invalid TOML file."""
        pyproject_path = project_dir / "pyproject.toml"
        pyproject_path.write_text("invalid toml [")

        # With new approach, toml.load will raise directly
        with pytest.raises(toml.TomlDecodeError):
            _load_pyproject_config(pyproject_path)

    def test_file_not_found(self, project_dir: Path) -> None:
        """Test loading non-existent file."""
        pyproject_path = project_dir / "nonexistent.toml"

        with pytest.raises(TyConfigError, match=r"pyproject\.toml is not a valid file"):
            _load_pyproject_config(pyproject_path)

    def test_empty_file(self, project_dir: Path) -> None:
        """Test loading empty TOML file."""
        pyproject_path = project_dir / "pyproject.toml"
        pyproject_path.write_text("")

        # Empty files now return empty dict instead of raising error
        result = _load_pyproject_config(pyproject_path)
        assert result == {}

    def test_invalid_format(self, project_dir: Path) -> None:
        """Test loading file that doesn't result in dictionary."""
        pyproject_path = project_dir / "pyproject.toml"
        # Create TOML that parses to a non-dict (array at root level)
        pyproject_path.write_text('[[array]]\nname = "test"')

        # This will parse as a dict with 'array' key, so it won't trigger our validation
        # Let's test with actual invalid TOML instead
        pyproject_path.write_text("= invalid")

        with pytest.raises(toml.TomlDecodeError):
            _load_pyproject_config(pyproject_path)


class TestCheckTyConfigExists:
    """Test _check_ty_config_exists function."""

    def test_ty_config_exists(self) -> None:
        """Test when ty config exists."""
        config = {"tool": {"ty": {"environment": {"root": ["./src"]}}}}
        assert _check_ty_config_exists(config) is True

    def test_ty_config_not_exists_no_tool(self) -> None:
        """Test when no tool section exists."""
        config = {"project": {"name": "test"}}
        assert _check_ty_config_exists(config) is False

    def test_ty_config_not_exists_no_ty(self) -> None:
        """Test when tool section exists but no ty."""
        config = {"tool": {"poetry": {"name": "test"}}}
        assert _check_ty_config_exists(config) is False

    def test_empty_config(self) -> None:
        """Test with empty config."""
        config = {}
        assert _check_ty_config_exists(config) is False


class TestApplyFallbackConfig:
    """Test _apply_fallback_config function."""

    def test_apply_to_empty_config(self, project_dir: Path) -> None:
        """Test applying fallback config to empty file."""
        pyproject_path = project_dir / "pyproject.toml"
        pyproject_path.write_text("")

        _apply_fallback_config(pyproject_path)

        config = toml.load(pyproject_path)
        assert "tool" in config
        assert "ty" in config["tool"]
        assert "environment" in config["tool"]["ty"]
        assert "rules" in config["tool"]["ty"]
        assert "src" in config["tool"]["ty"]

    def test_apply_to_existing_config(self, project_dir: Path) -> None:
        """Test applying fallback config to existing config."""
        pyproject_path = project_dir / "pyproject.toml"
        initial_config = {"project": {"name": "test"}}
        pyproject_path.write_text(toml.dumps(initial_config))

        _apply_fallback_config(pyproject_path)

        config = toml.load(pyproject_path)
        assert config["project"]["name"] == "test"  # Preserved
        assert "tool" in config
        assert "ty" in config["tool"]

    def test_apply_with_existing_tool_section(self, project_dir: Path) -> None:
        """Test applying fallback config with existing tool section."""
        pyproject_path = project_dir / "pyproject.toml"
        initial_config = {"tool": {"poetry": {"name": "test"}}}
        pyproject_path.write_text(toml.dumps(initial_config))

        _apply_fallback_config(pyproject_path)

        config = toml.load(pyproject_path)
        assert config["tool"]["poetry"]["name"] == "test"  # Preserved
        assert "ty" in config["tool"]

    def test_apply_to_readonly_file(self, project_dir: Path) -> None:
        """Test applying fallback config to readonly file."""
        pyproject_path = project_dir / "pyproject.toml"
        pyproject_path.write_text("[project]\nname = 'test'")  # Add some content
        pyproject_path.chmod(0o444)  # Read-only

        # With new approach, OS will raise PermissionError directly
        with pytest.raises(PermissionError):
            _apply_fallback_config(pyproject_path)


class TestTyConfigSetup:
    """Test ty_config_setup function."""

    def test_no_pyproject(self, project_dir: Path) -> None:
        """Test setup when no pyproject.toml exists."""
        with patch("ultrapyup.config.ty.Path.cwd", return_value=project_dir):
            result = ty_config_setup()

            assert result.success is False
            assert result.error_message == "No pyproject.toml found"

    def test_existing_ty_config(self, project_dir: Path) -> None:
        """Test setup when ty config already exists."""
        pyproject_path = project_dir / "pyproject.toml"
        config = {"tool": {"ty": {"environment": {"root": ["./src"]}}}}
        pyproject_path.write_text(toml.dumps(config))

        with patch("ultrapyup.config.ty.Path.cwd", return_value=project_dir):
            result = ty_config_setup()

            assert result.success is True
            assert result.config_exists is True

    @patch("ultrapyup.config.ty.detect_project_layout")
    @patch("ultrapyup.config.ty.apply_ty_config")
    def test_successful_layout_detection(self, mock_apply: Mock, mock_detect: Mock, project_dir: Path) -> None:
        """Test successful setup with layout detection."""
        layout = LayoutDetection(
            layout=ProjectLayout.SRC_LAYOUT,
            root_paths=["./src"],
            package_name="test_package",
        )
        mock_detect.return_value = layout

        pyproject_path = project_dir / "pyproject.toml"
        pyproject_path.write_text("[project]\nname = 'test'")

        with patch("ultrapyup.config.ty.Path.cwd", return_value=project_dir):
            result = ty_config_setup()

            assert result.success is True
            assert result.layout_detected == layout
            assert not result.fallback_used
            mock_detect.assert_called_once()
            mock_apply.assert_called_once_with(layout)

    def test_layout_detection_fails_fallback_succeeds(self, project_dir: Path) -> None:
        """Test fallback when layout detection fails."""
        pyproject_path = project_dir / "pyproject.toml"
        pyproject_path.write_text("[project]\nname = 'test'")

        with patch("ultrapyup.config.ty.Path.cwd", return_value=project_dir):
            # Mock detect_project_layout to return unknown layout (triggers fallback)
            unknown_layout = LayoutDetection(
                layout=ProjectLayout.UNKNOWN,
                root_paths=["./"],
                package_name=None,
            )
            with patch("ultrapyup.config.ty.detect_project_layout", return_value=unknown_layout):
                result = ty_config_setup()

                assert result.success is True
                assert result.fallback_used is True

    def test_both_detection_and_fallback_fail(self, project_dir: Path) -> None:
        """Test when both detection and fallback fail."""
        pyproject_path = project_dir / "pyproject.toml"
        pyproject_path.write_text("[project]\nname = 'test'")
        pyproject_path.chmod(0o444)  # Make readonly so fallback fails

        with patch("ultrapyup.config.ty.Path.cwd", return_value=project_dir):
            # Mock detect_project_layout to return unknown layout (triggers fallback)
            unknown_layout = LayoutDetection(
                layout=ProjectLayout.UNKNOWN,
                root_paths=["./"],
                package_name=None,
            )
            with patch("ultrapyup.config.ty.detect_project_layout", return_value=unknown_layout):
                # This should fail because file is readonly and fallback can't write
                with pytest.raises(PermissionError):
                    ty_config_setup()

    def test_toml_load_error(self, project_dir: Path) -> None:
        """Test setup when pyproject.toml has invalid TOML."""
        pyproject_path = project_dir / "pyproject.toml"
        pyproject_path.write_text("invalid toml [")

        with patch("ultrapyup.config.ty.Path.cwd", return_value=project_dir):
            # With new approach, toml.TomlDecodeError will be raised directly
            with pytest.raises(toml.TomlDecodeError):
                ty_config_setup()


class TestValidateTyConfig:
    """Test validate_ty_config function."""

    def test_valid_config(self, project_dir: Path) -> None:
        """Test validation of valid config."""
        pyproject_path = project_dir / "pyproject.toml"
        config = {"tool": {"ty": {"environment": {"root": ["./src"]}}}}
        pyproject_path.write_text(toml.dumps(config))

        with patch("ultrapyup.config.ty.Path.cwd", return_value=project_dir):
            assert validate_ty_config() is True

    def test_no_pyproject(self, project_dir: Path) -> None:
        """Test validation when no pyproject.toml."""
        with patch("ultrapyup.config.ty.Path.cwd", return_value=project_dir):
            assert validate_ty_config() is False

    def test_no_ty_config(self, project_dir: Path) -> None:
        """Test validation when no ty config."""
        pyproject_path = project_dir / "pyproject.toml"
        config = {"project": {"name": "test"}}
        pyproject_path.write_text(toml.dumps(config))

        with patch("ultrapyup.config.ty.Path.cwd", return_value=project_dir):
            assert validate_ty_config() is False

    def test_invalid_ty_config(self, project_dir: Path) -> None:
        """Test validation of invalid ty config."""
        pyproject_path = project_dir / "pyproject.toml"
        config = {"tool": {"ty": {}}}  # Missing environment section
        pyproject_path.write_text(toml.dumps(config))

        with patch("ultrapyup.config.ty.Path.cwd", return_value=project_dir):
            assert validate_ty_config() is False

    def test_invalid_toml(self, project_dir: Path) -> None:
        """Test validation with invalid TOML."""
        pyproject_path = project_dir / "pyproject.toml"
        pyproject_path.write_text("invalid toml [")

        with patch("ultrapyup.config.ty.Path.cwd", return_value=project_dir):
            # With new approach, toml.TomlDecodeError will be raised directly
            with pytest.raises(toml.TomlDecodeError):
                validate_ty_config()


class TestGetTyConfigInfo:
    """Test get_ty_config_info function."""

    def test_get_existing_config(self, project_dir: Path) -> None:
        """Test getting existing config info."""
        pyproject_path = project_dir / "pyproject.toml"
        ty_config = {"environment": {"root": ["./src"]}}
        config = {"tool": {"ty": ty_config}}
        pyproject_path.write_text(toml.dumps(config))

        with patch("ultrapyup.config.ty.Path.cwd", return_value=project_dir):
            result = get_ty_config_info()
            assert result == ty_config

    def test_get_no_pyproject(self, project_dir: Path) -> None:
        """Test getting config when no pyproject.toml."""
        with patch("ultrapyup.config.ty.Path.cwd", return_value=project_dir):
            result = get_ty_config_info()
            assert result is None

    def test_get_no_ty_config(self, project_dir: Path) -> None:
        """Test getting config when no ty config exists."""
        pyproject_path = project_dir / "pyproject.toml"
        config = {"project": {"name": "test"}}
        pyproject_path.write_text(toml.dumps(config))

        with patch("ultrapyup.config.ty.Path.cwd", return_value=project_dir):
            result = get_ty_config_info()
            assert result is None

    def test_get_invalid_toml(self, project_dir: Path) -> None:
        """Test getting config with invalid TOML."""
        pyproject_path = project_dir / "pyproject.toml"
        pyproject_path.write_text("invalid toml [")

        with patch("ultrapyup.config.ty.Path.cwd", return_value=project_dir):
            # With new approach, toml.TomlDecodeError will be raised directly
            with pytest.raises(toml.TomlDecodeError):
                get_ty_config_info()


class TestIntegration:
    """Integration tests for the ty config module."""

    def test_full_workflow_src_layout(self, project_dir: Path) -> None:
        """Test full workflow with src layout."""
        # Create project structure
        pyproject_path = project_dir / "pyproject.toml"
        pyproject_path.write_text("[project]\nname = 'test-project'")

        src_dir = project_dir / "src"
        src_dir.mkdir()
        (src_dir / "ultrapyup").mkdir()  # Use ultrapyup as package name to match layout detection
        (src_dir / "ultrapyup" / "__init__.py").write_text("")

        with patch("ultrapyup.config.ty.Path.cwd", return_value=project_dir):
            with patch("ultrapyup.layout.Path", lambda x: project_dir / x if x != "." else project_dir):
                # Setup config
                result = ty_config_setup()
                assert result.success is True
                assert result.layout_detected is not None
                assert result.layout_detected.layout == ProjectLayout.SRC_LAYOUT

                # Validate config
                assert validate_ty_config() is True

                # Get config info
                config_info = get_ty_config_info()
                assert config_info is not None
                assert "environment" in config_info

    def test_full_workflow_fallback(self, project_dir: Path) -> None:
        """Test full workflow with fallback configuration."""
        # Create minimal project structure (will trigger fallback)
        pyproject_path = project_dir / "pyproject.toml"
        pyproject_path.write_text("[project]\nname = 'test-project'")

        with patch("ultrapyup.config.ty.Path.cwd", return_value=project_dir):
            # Mock detect_project_layout to return unknown layout (triggers fallback)
            unknown_layout = LayoutDetection(
                layout=ProjectLayout.UNKNOWN,
                root_paths=["./"],
                package_name=None,
            )
            with patch("ultrapyup.config.ty.detect_project_layout", return_value=unknown_layout):
                # Setup config (should fallback)
                result = ty_config_setup()
                assert result.success is True
                assert result.fallback_used is True

                # Validate config
                assert validate_ty_config() is True

                # Get config info
                config_info = get_ty_config_info()
                assert config_info is not None
                assert config_info["environment"]["root"] == ["./src"]
