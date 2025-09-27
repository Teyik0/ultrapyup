from pathlib import Path
from unittest.mock import patch

import pytest
import toml
from _pytest.capture import CaptureResult

from ultrapyup.config.ty import _create_ty_config, _ty_conf_exist, ty_config_setup
from ultrapyup.layout import LayoutDetection, ProjectLayout


def _assert_ty_conf_skipped(captured: CaptureResult[str]) -> None:
    assert "Keeping existing configuration" in captured.out


def _assert_ty_conf_overwritten(captured: CaptureResult[str]) -> None:
    assert "ty configuration updated in pyproject.toml" in captured.out


def _assert_ty_conf_complete(captured: CaptureResult[str]) -> None:
    assert "Ty configuration setup completed" in captured.out
    assert "ty configuration added to pyproject.toml" in captured.out


def _clean_ty_conf() -> Path:
    pyproject_file = Path.cwd() / "pyproject.toml"
    if pyproject_file.exists():
        pyproject_file.unlink()
    return pyproject_file


def _get_expected_ty_config() -> dict:
    return {
        "environment": {"root": ["./src"]},
    }


def _get_default_layout() -> LayoutDetection:
    """Get a default layout for testing."""
    return LayoutDetection(layout=ProjectLayout.SRC_LAYOUT, root_paths=["./src"], package_name="test_package")


class TestTyConfExist:
    """Tests for _ty_conf_exist function."""

    def test_pyproject_toml_with_ty_config(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test when pyproject.toml contains [tool.ty] section."""
        pyproject_file = Path.cwd() / "pyproject.toml"
        config = {"tool": {"ty": {"environment": {"root": ["./src"]}}}}
        with open(pyproject_file, "w") as f:
            toml.dump(config, f)

        assert _ty_conf_exist() is True

    def test_pyproject_toml_without_ty_config(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test when pyproject.toml exists but has no [tool.ty] section."""
        pyproject_file = Path.cwd() / "pyproject.toml"
        config = {"tool": {"ruff": {"line-length": 88}}}
        with open(pyproject_file, "w") as f:
            toml.dump(config, f)

        assert _ty_conf_exist() is False

    def test_pyproject_toml_does_not_exist(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test when pyproject.toml doesn't exist."""
        pyproject_file = Path.cwd() / "pyproject.toml"
        if pyproject_file.exists():
            pyproject_file.unlink()

        assert _ty_conf_exist() is False

    def test_empty_pyproject_toml(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test when pyproject.toml is empty."""
        pyproject_file = Path.cwd() / "pyproject.toml"
        pyproject_file.write_text("")

        assert _ty_conf_exist() is False

    def test_malformed_pyproject_toml(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test when pyproject.toml is malformed."""
        pyproject_file = Path.cwd() / "pyproject.toml"
        pyproject_file.write_text("invalid toml content [")

        with pytest.raises(toml.TomlDecodeError):
            _ty_conf_exist()


class TestCreateTyConfig:
    """Tests for _create_ty_config function."""

    def test_create_ty_config_success(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test successful creation of ty config in pyproject.toml."""
        pyproject_file = Path.cwd() / "pyproject.toml"
        if pyproject_file.exists():
            pyproject_file.unlink()

        _create_ty_config(_get_default_layout())

        assert pyproject_file.exists()
        with open(pyproject_file) as f:
            config = toml.load(f)
        assert "tool" in config
        assert "ty" in config["tool"]
        assert config["tool"]["ty"] == _get_expected_ty_config()

    def test_create_ty_config_with_existing_pyproject(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test creation of ty config when pyproject.toml already exists with other tools."""
        pyproject_file = Path.cwd() / "pyproject.toml"
        existing_config = {"tool": {"ruff": {"line-length": 88}}}
        with open(pyproject_file, "w") as f:
            toml.dump(existing_config, f)

        _create_ty_config(_get_default_layout())

        with open(pyproject_file) as f:
            config = toml.load(f)
        assert "tool" in config
        assert "ty" in config["tool"]
        assert "ruff" in config["tool"]  # Original config preserved
        assert config["tool"]["ty"] == _get_expected_ty_config()
        assert config["tool"]["ruff"]["line-length"] == 88

    def test_create_ty_config_overwrites_existing_ty(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test that _create_ty_config overwrites existing ty config."""
        pyproject_file = Path.cwd() / "pyproject.toml"
        config = {"tool": {"ty": {"old": "config"}}}
        with open(pyproject_file, "w") as f:
            toml.dump(config, f)

        _create_ty_config(_get_default_layout())

        with open(pyproject_file) as f:
            updated_config = toml.load(f)
        assert updated_config["tool"]["ty"] == _get_expected_ty_config()
        assert "old" not in updated_config["tool"]["ty"]


class TestTyConfigSetup:
    """Tests for ty_config_setup function."""

    def test_ty_config_setup_when_config_exists_user_says_no(
        self,
        project_dir: Path,  # noqa: ARG002
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test ty_config_setup when configuration exists and user chooses not to overwrite."""
        pyproject_file = Path.cwd() / "pyproject.toml"
        original_config = {"tool": {"ty": {"old": "config"}}}
        with open(pyproject_file, "w") as f:
            toml.dump(original_config, f)

        with patch("ultrapyup.config.ty.ask") as mock_ask:
            mock_ask.return_value = "no"
            result = ty_config_setup(_get_default_layout())

            assert result is None
            with open(pyproject_file) as f:
                config = toml.load(f)
            assert config == original_config
            mock_ask.assert_called_once_with(
                "Ty configuration already exists. Do you want to overwrite it?",
                choices=["yes", "no"],
                multiselect=False,
            )
            _assert_ty_conf_skipped(capsys.readouterr())

    def test_ty_config_setup_when_config_exists_user_says_yes(
        self,
        project_dir: Path,  # noqa: ARG002
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test ty_config_setup when configuration exists and user chooses to overwrite."""
        pyproject_file = Path.cwd() / "pyproject.toml"
        config = {"tool": {"ty": {"old": "config"}}}
        with open(pyproject_file, "w") as f:
            toml.dump(config, f)

        with patch("ultrapyup.config.ty.ask") as mock_ask:
            mock_ask.return_value = "yes"
            result = ty_config_setup(_get_default_layout())

            assert result is None
            with open(pyproject_file) as f:
                updated_config = toml.load(f)
            assert updated_config["tool"]["ty"] == _get_expected_ty_config()
            mock_ask.assert_called_once_with(
                "Ty configuration already exists. Do you want to overwrite it?",
                choices=["yes", "no"],
                multiselect=False,
            )
            _assert_ty_conf_overwritten(capsys.readouterr())

    def test_ty_config_setup_when_no_config_exists(
        self,
        project_dir: Path,  # noqa: ARG002
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test ty_config_setup when no configuration exists."""
        pyproject_file = _clean_ty_conf()

        result = ty_config_setup(_get_default_layout())

        assert result is None
        assert pyproject_file.exists()
        with open(pyproject_file) as f:
            config = toml.load(f)
        assert "tool" in config
        assert "ty" in config["tool"]
        assert config["tool"]["ty"] == _get_expected_ty_config()
        _assert_ty_conf_complete(capsys.readouterr())

    def test_ty_config_setup_preserves_existing_config_when_user_says_no(
        self,
        project_dir: Path,  # noqa: ARG002
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test that ty_config_setup doesn't overwrite existing configuration when user says no."""
        pyproject_file = Path.cwd() / "pyproject.toml"
        original_config = {"tool": {"ty": {"custom": "settings"}, "ruff": {"line-length": 88}}}
        with open(pyproject_file, "w") as f:
            toml.dump(original_config, f)

        with patch("ultrapyup.config.ty.ask") as mock_ask:
            mock_ask.return_value = "no"
            ty_config_setup(_get_default_layout())
            with open(pyproject_file) as f:
                config = toml.load(f)
            assert config == original_config
            _assert_ty_conf_skipped(capsys.readouterr())

    def test_ty_config_setup_creates_pyproject_when_none_exists(
        self,
        project_dir: Path,  # noqa: ARG002
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test that ty_config_setup creates pyproject.toml when it doesn't exist."""
        pyproject_file = _clean_ty_conf()
        assert not pyproject_file.exists()

        with patch("ultrapyup.config.ty.ask") as mock_ask:
            mock_ask.return_value = "yes"  # Should not be called, but just in case
            ty_config_setup(_get_default_layout())

            assert pyproject_file.exists()
            with open(pyproject_file) as f:
                config = toml.load(f)
            assert "tool" in config
            assert "ty" in config["tool"]
            assert config["tool"]["ty"] == _get_expected_ty_config()
            _assert_ty_conf_complete(capsys.readouterr())


class TestTyConfigEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_concurrent_ty_config_setup(self, project_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:  # noqa: ARG002
        """Test that multiple consecutive setups work correctly."""
        # First call should create the config (no existing config)
        pyproject_file = _clean_ty_conf()
        result = ty_config_setup(_get_default_layout())
        assert result is None
        assert pyproject_file.exists()
        with open(pyproject_file) as f:
            config = toml.load(f)
        assert config["tool"]["ty"] == _get_expected_ty_config()
        _assert_ty_conf_complete(capsys.readouterr())

        # Second call should prompt user (config now exists)
        with patch("ultrapyup.config.ty.ask") as mock_ask:
            mock_ask.return_value = "no"
            ty_config_setup(_get_default_layout())
            assert result is None
            assert pyproject_file.exists()
            with open(pyproject_file) as f:
                config = toml.load(f)
            assert config["tool"]["ty"] == _get_expected_ty_config()
            mock_ask.assert_called_once_with(
                "Ty configuration already exists. Do you want to overwrite it?",
                choices=["yes", "no"],
                multiselect=False,
            )
            _assert_ty_conf_skipped(capsys.readouterr())

    def test_ty_config_setup_with_different_layouts(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test that ty_config_setup uses different root paths based on layout."""
        pyproject_file = _clean_ty_conf()

        # Test with flat layout
        flat_layout = LayoutDetection(layout=ProjectLayout.FLAT_LAYOUT, root_paths=["./"], package_name=None)
        ty_config_setup(flat_layout)

        with open(pyproject_file) as f:
            config = toml.load(f)
        assert config["tool"]["ty"]["environment"]["root"] == ["./"]

        # Clean and test with app layout
        pyproject_file.unlink()
        app_layout = LayoutDetection(layout=ProjectLayout.APP_LAYOUT, root_paths=["./app"], package_name="myapp")
        ty_config_setup(app_layout)

        with open(pyproject_file) as f:
            config = toml.load(f)
        assert config["tool"]["ty"]["environment"]["root"] == ["./app"]

        # Clean and test with package layout
        pyproject_file.unlink()
        package_layout = LayoutDetection(
            layout=ProjectLayout.PACKAGE_LAYOUT, root_paths=["./mypackage"], package_name="mypackage"
        )
        ty_config_setup(package_layout)

        with open(pyproject_file) as f:
            config = toml.load(f)
        assert config["tool"]["ty"]["environment"]["root"] == ["./mypackage"]
