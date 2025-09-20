from pathlib import Path

import pytest
import toml
from _pytest.capture import CaptureResult

from ultrapyup.config.ruff import _create_ruff_config, _ruff_conf_exist, ruff_config_setup


def _assert_ruff_conf_already_exist(captured: CaptureResult[str]) -> None:
    assert "Ruff configuration setup skipped" in captured.out
    assert "Ruff configuration already exists, skipping" in captured.out


def _assert_ruff_conf_complete(captured: CaptureResult[str]) -> None:
    assert "Ruff configuration setup completed" in captured.out
    assert "ruff.toml created" in captured.out


def _clean_ruff_conf() -> tuple[Path, Path]:
    ruff_file = Path.cwd() / "ruff.toml"
    pyproject_file = Path.cwd() / "pyproject.toml"
    if ruff_file.exists():
        ruff_file.unlink()
    if pyproject_file.exists():
        pyproject_file.unlink()

    return ruff_file, pyproject_file


ruff_toml_resource_file = Path(__file__).parent.parent.parent / "src/ultrapyup/resources/ruff.toml"
if not ruff_toml_resource_file.exists():
    raise FileNotFoundError(f"Resource file {ruff_toml_resource_file} does not exist.")


class TestRuffConfExist:
    """Tests for _ruff_conf_exist function."""

    def test_ruff_toml_exists(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test when ruff.toml exists in current directory."""
        # Create ruff.toml file
        ruff_file = Path.cwd() / "ruff.toml"
        ruff_file.write_text("line-length = 88")

        assert _ruff_conf_exist() is True

    def test_ruff_toml_does_not_exist(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test when ruff.toml doesn't exist."""
        # Ensure ruff.toml doesn't exist
        ruff_file = Path.cwd() / "ruff.toml"
        if ruff_file.exists():
            ruff_file.unlink()

        # Ensure pyproject.toml doesn't exist or doesn't have ruff config
        pyproject_file = Path.cwd() / "pyproject.toml"
        if pyproject_file.exists():
            pyproject_file.unlink()

        assert _ruff_conf_exist() is False

    def test_pyproject_toml_with_ruff_config(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test when pyproject.toml contains [tool.ruff] section."""
        pyproject_file = Path.cwd() / "pyproject.toml"
        config = {"tool": {"ruff": {"line-length": 88, "target-version": "py39"}}}
        with open(pyproject_file, "w") as f:
            toml.dump(config, f)

        assert _ruff_conf_exist() is True

    def test_pyproject_toml_without_ruff_config(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test when pyproject.toml exists but has no [tool.ruff] section."""
        pyproject_file = Path.cwd() / "pyproject.toml"
        config = {"tool": {"black": {"line-length": 88}}}
        with open(pyproject_file, "w") as f:
            toml.dump(config, f)

        assert _ruff_conf_exist() is False

    def test_both_ruff_toml_and_pyproject_ruff_exist(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test when both ruff.toml and pyproject.toml with ruff config exist."""
        # Create ruff.toml
        ruff_file = Path.cwd() / "ruff.toml"
        ruff_file.write_text("line-length = 88")

        # Create pyproject.toml with ruff config
        pyproject_file = Path.cwd() / "pyproject.toml"
        config = {"tool": {"ruff": {"line-length": 100}}}
        with open(pyproject_file, "w") as f:
            toml.dump(config, f)

        # Should return True because ruff.toml exists (checked first)
        assert _ruff_conf_exist() is True

    def test_empty_pyproject_toml(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test when pyproject.toml is empty."""
        pyproject_file = Path.cwd() / "pyproject.toml"
        pyproject_file.write_text("")

        assert _ruff_conf_exist() is False

    def test_malformed_pyproject_toml(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test when pyproject.toml is malformed."""
        pyproject_file = Path.cwd() / "pyproject.toml"
        pyproject_file.write_text("invalid toml content [")

        # Should raise an exception when trying to parse malformed TOML
        with pytest.raises(toml.TomlDecodeError):
            _ruff_conf_exist()


class TestCreateRuffConfig:
    """Tests for _create_ruff_config function."""

    def test_create_ruff_config_success(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test successful creation of ruff.toml file."""
        # Ensure ruff.toml doesn't exist initially
        ruff_file = Path.cwd() / "ruff.toml"
        if ruff_file.exists():
            ruff_file.unlink()

        _create_ruff_config()

        assert ruff_file.exists()
        assert ruff_file.read_text() == ruff_toml_resource_file.read_text()


class TestRuffConfigSetup:
    """Tests for ruff_config_setup function."""

    def test_ruff_config_setup_when_config_exists(self, project_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:  # noqa: ARG002
        """Test ruff_config_setup when configuration already exists."""
        # Create existing ruff.toml
        ruff_file = Path.cwd() / "ruff.toml"
        ruff_file.write_text("line-length = 88")

        result = ruff_config_setup()

        assert result is None
        assert ruff_file.read_text() != ruff_toml_resource_file.read_text()
        _assert_ruff_conf_already_exist(capsys.readouterr())

    def test_ruff_config_setup_when_pyproject_config_exists(
        self,
        project_dir: Path,  # noqa: ARG002
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test ruff_config_setup when pyproject.toml has ruff config."""
        # Create pyproject.toml with ruff config
        pyproject_file = Path.cwd() / "pyproject.toml"
        config = {"tool": {"ruff": {"line-length": 100, "target-version": "py310"}}}
        with open(pyproject_file, "w") as f:
            toml.dump(config, f)

        result = ruff_config_setup()

        assert result is None
        assert not (Path.cwd() / "ruff.toml").exists()
        _assert_ruff_conf_already_exist(capsys.readouterr())

    def test_ruff_config_setup_when_no_config_exists(
        self,
        project_dir: Path,  # noqa: ARG002
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test ruff_config_setup when no configuration exists."""
        ruff_file, _ = _clean_ruff_conf()
        result = ruff_config_setup()

        assert result is None
        assert ruff_file.exists()
        assert ruff_file.read_text() == ruff_toml_resource_file.read_text()
        _assert_ruff_conf_complete(capsys.readouterr())

    def test_ruff_config_setup_preserves_existing_config(
        self,
        project_dir: Path,  # noqa: ARG002
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test that ruff_config_setup doesn't overwrite existing configuration."""
        # Create existing ruff.toml with specific content
        ruff_file = Path.cwd() / "ruff.toml"
        original_content = "line-length = 88\nexisting = true"
        ruff_file.write_text(original_content)

        ruff_config_setup()

        # Verify config was not changed
        assert ruff_file.exists()
        content = ruff_file.read_text()
        assert content == original_content
        assert content != ruff_toml_resource_file.read_text()
        _assert_ruff_conf_already_exist(capsys.readouterr())


class TestRuffConfigEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_concurrent_ruff_config_setup(self, project_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:  # noqa: ARG002
        """Test that multiple consecutive setups work correctly."""
        # First call should create the config
        ruff_file, _ = _clean_ruff_conf()
        result = ruff_config_setup()
        assert result is None
        assert ruff_file.exists()
        assert ruff_file.read_text() == ruff_toml_resource_file.read_text()
        _assert_ruff_conf_complete(capsys.readouterr())

        # Second call should skip (config now exists)
        ruff_config_setup()
        assert result is None
        assert ruff_file.exists()
        assert ruff_file.read_text() == ruff_toml_resource_file.read_text()
        _assert_ruff_conf_already_exist(capsys.readouterr())
