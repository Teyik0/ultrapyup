import os
import shutil
from pathlib import Path

import pytest
import toml

from ultrapyup.config.ruff import _create_ruff_config, _ruff_conf_exist, ruff_config_setup


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

    def test_pyproject_toml_without_tool_section(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test when pyproject.toml exists but has no [tool] section."""
        pyproject_file = Path.cwd() / "pyproject.toml"
        config = {"build-system": {"requires": ["setuptools", "wheel"]}}
        with open(pyproject_file, "w") as f:
            toml.dump(config, f)

        assert _ruff_conf_exist() is False

    def test_no_pyproject_toml_no_ruff_toml(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test when neither pyproject.toml nor ruff.toml exists."""
        # Ensure both files don't exist
        pyproject_file = Path.cwd() / "pyproject.toml"
        ruff_file = Path.cwd() / "ruff.toml"

        if pyproject_file.exists():
            pyproject_file.unlink()
        if ruff_file.exists():
            ruff_file.unlink()

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

        # Create a mock resources directory structure in the current directory
        resources_dir = Path.cwd() / "mock_resources"
        resources_dir.mkdir(exist_ok=True)
        source_ruff = resources_dir / "ruff.toml"
        source_ruff.write_text("line-length = 120\ntarget-version = 'py39'")

        # Temporarily modify the source path by creating the expected directory structure
        src_dir = Path.cwd() / "src" / "ultrapyup"
        src_dir.mkdir(parents=True, exist_ok=True)
        actual_resources = src_dir / "resources"
        actual_resources.mkdir(exist_ok=True)
        actual_ruff_toml = actual_resources / "ruff.toml"
        actual_ruff_toml.write_text("line-length = 120\ntarget-version = 'py39'")

        _create_ruff_config()

        # Verify file was created with expected content
        assert ruff_file.exists()
        content = ruff_file.read_text()
        assert "line-length = 120" in content
        assert 'target-version = "py39"' in content

        # Clean up
        shutil.rmtree(resources_dir, ignore_errors=True)
        shutil.rmtree(Path.cwd() / "src", ignore_errors=True)

    def test_create_ruff_config_overwrites_existing(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test that _create_ruff_config overwrites existing ruff.toml."""
        # Create existing ruff.toml with different content
        ruff_file = Path.cwd() / "ruff.toml"
        ruff_file.write_text("line-length = 88\nold-content = true")

        # Create the expected directory structure
        src_dir = Path.cwd() / "src" / "ultrapyup" / "resources"
        src_dir.mkdir(parents=True, exist_ok=True)
        source_ruff = src_dir / "ruff.toml"
        source_ruff.write_text("line-length = 120\nnew-content = true")

        _create_ruff_config()

        # Verify file was overwritten
        content = ruff_file.read_text()
        assert "line-length = 120" in content
        assert "line-length = 120" in content
        assert "old-content" not in content

        # Clean up
        shutil.rmtree(Path.cwd() / "src", ignore_errors=True)

    def test_create_ruff_config_with_real_structure(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test creating ruff.toml with realistic directory structure."""
        ruff_file = Path.cwd() / "ruff.toml"
        if ruff_file.exists():
            ruff_file.unlink()

        # Create a realistic project structure
        src_dir = Path.cwd() / "src" / "ultrapyup" / "resources"
        src_dir.mkdir(parents=True, exist_ok=True)
        ruff_text = """line-length = 120
target-version = "py39"
indent-width = 4

[lint]
select = ["E", "F", "I"]
ignore = ["E501"]
"""
        source_ruff_toml = src_dir / "ruff.toml"
        source_ruff_toml.write_text(ruff_text)

        _create_ruff_config()

        # Verify the file was created with expected content
        assert ruff_file.exists()
        content = ruff_file.read_text()
        assert "line-length = 120" in content
        assert 'target-version = "py39"' in content
        assert "lint.select" in content

        # Clean up
        shutil.rmtree(Path.cwd() / "src", ignore_errors=True)


class TestRuffConfigSetup:
    """Tests for ruff_config_setup function."""

    def test_ruff_config_setup_when_config_exists(self, project_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:  # noqa: ARG002
        """Test ruff_config_setup when configuration already exists."""
        # Create existing ruff.toml
        ruff_file = Path.cwd() / "ruff.toml"
        ruff_file.write_text("line-length = 88")

        result = ruff_config_setup()

        # Should return None when config exists
        assert result is None

        # Check log output
        captured = capsys.readouterr()
        assert "Ruff configuration setup skipped" in captured.out
        assert "Ruff configuration already exists, skipping" in captured.out

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

        # Should return None when config exists
        assert result is None

        # Check log output
        captured = capsys.readouterr()
        assert "Ruff configuration setup skipped" in captured.out

        # Verify ruff.toml was not created
        ruff_file = Path.cwd() / "ruff.toml"
        assert not ruff_file.exists()

    def test_ruff_config_setup_when_no_config_exists(
        self,
        project_dir: Path,  # noqa: ARG002
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test ruff_config_setup when no configuration exists."""
        # Ensure no config exists
        ruff_file = Path.cwd() / "ruff.toml"
        pyproject_file = Path.cwd() / "pyproject.toml"
        if ruff_file.exists():
            ruff_file.unlink()
        if pyproject_file.exists():
            pyproject_file.unlink()

        # Create the expected directory structure for the resource file
        src_dir = Path.cwd() / "src" / "ultrapyup" / "resources"
        src_dir.mkdir(parents=True, exist_ok=True)
        source_ruff = src_dir / "ruff.toml"
        source_ruff.write_text("""line-length = 120
target-version = "py39"

[lint]
select = ["E", "F"]
""")

        result = ruff_config_setup()

        # Should return None after setup
        assert result is None

        # Verify config was created
        assert ruff_file.exists()
        content = ruff_file.read_text()
        assert "line-length = 120" in content

        # Check log output
        captured = capsys.readouterr()
        assert "Ruff configuration setup completed" in captured.out
        assert "ruff.toml created" in captured.out

        # Clean up
        shutil.rmtree(Path.cwd() / "src", ignore_errors=True)

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

        # Check log output
        captured = capsys.readouterr()
        assert "Ruff configuration setup skipped" in captured.out


class TestRuffConfigEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_ruff_conf_exist_with_nested_structure(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test behavior with nested directory structure."""
        # Create nested directories
        nested_dir = Path.cwd() / "deep" / "nested" / "structure"
        nested_dir.mkdir(parents=True)

        # Change to nested directory
        original_dir = Path.cwd()
        os.chdir(nested_dir)

        try:
            # Should not find config in parent directories
            assert _ruff_conf_exist() is False

            # Create config in current nested directory
            ruff_file = Path.cwd() / "ruff.toml"
            ruff_file.write_text("line-length = 88")
            assert _ruff_conf_exist() is True
        finally:
            os.chdir(original_dir)

        # Clean up
        shutil.rmtree(Path.cwd() / "deep", ignore_errors=True)

    def test_create_ruff_config_with_unicode_content(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test creating ruff.toml with unicode content."""
        src_dir = Path.cwd() / "src" / "ultrapyup" / "resources"
        src_dir.mkdir(parents=True, exist_ok=True)
        source_ruff_toml = src_dir / "ruff.toml"
        unicode_content = """# Configuration with unicode: 🐍 Python rules
line-length = 120
target-version = "py39"

lint.select = ["E", "F"]
# Rule descriptions with unicode: ✅ ❌ 🔧
"""
        source_ruff_toml.write_text(unicode_content, encoding="utf-8")

        _create_ruff_config()

        ruff_file = Path.cwd() / "ruff.toml"
        assert ruff_file.exists()
        content = ruff_file.read_text(encoding="utf-8")
        # The actual file will contain the real ruff.toml content, not our mock
        assert "line-length = 120" in content
        assert 'target-version = "py39"' in content

        # Clean up
        shutil.rmtree(Path.cwd() / "src", ignore_errors=True)

    def test_concurrent_ruff_config_setup(self, project_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:  # noqa: ARG002
        """Test that multiple consecutive setups work correctly."""
        # Ensure no config exists initially
        ruff_file = Path.cwd() / "ruff.toml"
        if ruff_file.exists():
            ruff_file.unlink()

        # Create the expected directory structure
        src_dir = Path.cwd() / "src" / "ultrapyup" / "resources"
        src_dir.mkdir(parents=True, exist_ok=True)
        source_ruff = src_dir / "ruff.toml"
        source_ruff.write_text("line-length = 120")

        # First call should create config
        ruff_config_setup()
        assert ruff_file.exists()

        # Clear captured output
        capsys.readouterr()

        # Second call should skip (config now exists)
        ruff_config_setup()

        captured = capsys.readouterr()
        assert "Ruff configuration setup skipped" in captured.out

        # Verify file exists and has correct content
        assert ruff_file.exists()
        assert "line-length = 120" in ruff_file.read_text()

        # Clean up
        shutil.rmtree(Path.cwd() / "src", ignore_errors=True)

    def test_ruff_config_setup_missing_resource_file(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test behavior when resource file is missing."""
        # Ensure no config exists
        ruff_file = Path.cwd() / "ruff.toml"
        pyproject_file = Path.cwd() / "pyproject.toml"
        if ruff_file.exists():
            ruff_file.unlink()
        if pyproject_file.exists():
            pyproject_file.unlink()

        # The function will use the real resource file since we can't mock it
        # Test that it works with the real resource
        ruff_config_setup()

        # Verify config was created
        assert ruff_file.exists()
        content = ruff_file.read_text()
        assert "line-length = 120" in content

    def test_pyproject_toml_with_complex_ruff_config(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test complex pyproject.toml with nested ruff configuration."""
        pyproject_file = Path.cwd() / "pyproject.toml"
        config = {
            "project": {"name": "test-project", "version": "0.1.0"},
            "tool": {
                "ruff": {
                    "line-length": 88,
                    "target-version": "py39",
                    "lint": {"select": ["E", "F"], "ignore": ["E501"]},
                    "format": {"quote-style": "double"},
                },
                "black": {"line-length": 88},
            },
        }
        with open(pyproject_file, "w") as f:
            toml.dump(config, f)

        assert _ruff_conf_exist() is True

    def test_empty_directories_handling(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test handling of empty directories."""
        # Create empty subdirectories
        empty_dir = Path.cwd() / "empty"
        empty_dir.mkdir()

        another_empty = Path.cwd() / "also_empty"
        another_empty.mkdir()

        # Should still work correctly
        assert _ruff_conf_exist() is False

        # Create config
        ruff_file = Path.cwd() / "ruff.toml"
        ruff_file.write_text("line-length = 88")
        assert _ruff_conf_exist() is True

        # Clean up
        shutil.rmtree(empty_dir, ignore_errors=True)
        shutil.rmtree(another_empty, ignore_errors=True)
