"""Tests for the pre_commit module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ultrapyup.pre_commit import (
    PreCommitTool,
    get_precommit_tool,
    options,
    precommit_setup,
)


class TestGetPrecommitTool:
    """Tests for get_precommit_tool function."""

    def test_select_lefthook(self, capsys):
        """Test selecting Lefthook as pre-commit tool."""
        with patch("ultrapyup.pre_commit.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = ["Lefthook"]

            result = get_precommit_tool()

            assert result is not None
            assert len(result) == 1
            assert result[0].name == "Lefthook"
            assert result[0].value == "lefthook"
            assert result[0].filename == "lefthook.yaml"

            captured = capsys.readouterr()
            assert "lefthook" in captured.out

    def test_select_precommit(self, capsys):
        """Test selecting Pre-commit as pre-commit tool."""
        with patch("ultrapyup.pre_commit.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = ["Pre-commit"]

            result = get_precommit_tool()

            assert result is not None
            assert len(result) == 1
            assert result[0].name == "Pre-commit"
            assert result[0].value == "pre-commit"
            assert result[0].filename == ".pre-commit-config.yaml"

            captured = capsys.readouterr()
            assert "pre-commit" in captured.out

    def test_select_multiple_tools(self, capsys):
        """Test selecting multiple pre-commit tools."""
        with patch("ultrapyup.pre_commit.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = ["Lefthook", "Pre-commit"]

            result = get_precommit_tool()

            assert result is not None
            assert len(result) == 2
            assert result[0].name == "Lefthook"
            assert result[1].name == "Pre-commit"

            captured = capsys.readouterr()
            assert "lefthook" in captured.out
            assert "pre-commit" in captured.out

    def test_skip_selection(self, capsys):
        """Test skipping pre-commit tool selection (Ctrl+C)."""
        with patch("ultrapyup.pre_commit.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = None

            result = get_precommit_tool()

            assert result is None

            captured = capsys.readouterr()
            assert "none" in captured.out

    def test_empty_selection(self, capsys):
        """Test empty selection (no tools selected)."""
        with patch("ultrapyup.pre_commit.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = []

            result = get_precommit_tool()

            assert result is None

            captured = capsys.readouterr()
            assert "none" in captured.out

    def test_inquirer_configuration(self):
        """Test that inquirer is configured correctly."""
        with patch("ultrapyup.pre_commit.inquirer.select") as mock_inquirer:
            mock_select = MagicMock()
            mock_inquirer.return_value = mock_select
            mock_select.execute.return_value = []

            get_precommit_tool()

            # Verify inquirer.select was called with correct parameters
            mock_inquirer.assert_called_once()
            call_args = mock_inquirer.call_args

            assert (
                "Which pre-commit tool would you like to use" in call_args[1]["message"]
            )
            assert call_args[1]["multiselect"] is True
            assert call_args[1]["mandatory"] is False
            assert "skip" in call_args[1]["keybindings"]
            assert call_args[1]["choices"] == ["Lefthook", "Pre-commit"]


class TestPrecommitSetup:
    """Tests for precommit_setup function."""

    def test_setup_lefthook(self, project_dir: Path):
        """Test setting up Lefthook."""
        pre_commit_tool = PreCommitTool("Lefthook", "lefthook", "lefthook.yaml")

        # Create mock resource file
        resources_dir = Path(__file__).parent.parent / "src" / "ultrapyup" / "resources"
        resources_dir.mkdir(parents=True, exist_ok=True)
        lefthook_source = resources_dir / "lefthook.yaml"
        lefthook_source.write_text(
            "# Lefthook config\npre-commit:\n  commands:\n    test: echo 'test'"
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0

            precommit_setup("uv add", pre_commit_tool)

            # Check file was copied
            assert (project_dir / "lefthook.yaml").exists()
            assert "Lefthook config" in (project_dir / "lefthook.yaml").read_text()

            # Check install command was run
            mock_run.assert_called_once_with(
                "uv add lefthook install",
                shell=True,
                capture_output=True,
            )

    def test_setup_precommit(self, project_dir: Path):
        """Test setting up Pre-commit."""
        pre_commit_tool = PreCommitTool(
            "Pre-commit", "pre-commit", ".pre-commit-config.yaml"
        )

        # Create mock resource file
        resources_dir = Path(__file__).parent.parent / "src" / "ultrapyup" / "resources"
        resources_dir.mkdir(parents=True, exist_ok=True)
        precommit_source = resources_dir / ".pre-commit-config.yaml"
        precommit_source.write_text(
            "repos:\n  - repo: local\n    hooks:\n      - id: test"
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0

            precommit_setup("pip install", pre_commit_tool)

            # Check file was copied
            assert (project_dir / ".pre-commit-config.yaml").exists()
            assert "repos:" in (project_dir / ".pre-commit-config.yaml").read_text()

            # Check install command was run
            mock_run.assert_called_once_with(
                "pip install pre-commit install",
                shell=True,
                capture_output=True,
            )

    def test_setup_with_existing_file(self, project_dir: Path):
        """Test setup overwrites existing pre-commit configuration file."""
        pre_commit_tool = PreCommitTool("Lefthook", "lefthook", "lefthook.yaml")

        # Create existing file
        existing_file = project_dir / "lefthook.yaml"
        existing_file.write_text("# Old config")

        # Create mock resource file
        resources_dir = Path(__file__).parent.parent / "src" / "ultrapyup" / "resources"
        resources_dir.mkdir(parents=True, exist_ok=True)
        lefthook_source = resources_dir / "lefthook.yaml"
        lefthook_source.write_text("# New Lefthook config")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0

            precommit_setup("uv add", pre_commit_tool)

            # Check file was overwritten
            assert (project_dir / "lefthook.yaml").exists()
            assert "New Lefthook config" in (project_dir / "lefthook.yaml").read_text()
            assert "Old config" not in (project_dir / "lefthook.yaml").read_text()

    def test_setup_preserves_file_permissions(self, project_dir: Path):
        """Test that setup preserves source file permissions."""
        import os
        import stat

        pre_commit_tool = PreCommitTool("Lefthook", "lefthook", "lefthook.yaml")

        # Create mock resource file with specific permissions
        resources_dir = Path(__file__).parent.parent / "src" / "ultrapyup" / "resources"
        resources_dir.mkdir(parents=True, exist_ok=True)
        lefthook_source = resources_dir / "lefthook.yaml"
        lefthook_source.write_text("# Lefthook config")

        # Set specific permissions on source
        os.chmod(
            lefthook_source, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
        )
        source_mode = lefthook_source.stat().st_mode

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0

            precommit_setup("uv add", pre_commit_tool)

            # Check permissions were preserved
            dest_file = project_dir / "lefthook.yaml"
            assert dest_file.exists()
            assert dest_file.stat().st_mode == source_mode

    def test_setup_with_subprocess_error(self, project_dir: Path):
        """Test setup handles subprocess errors gracefully."""
        pre_commit_tool = PreCommitTool("Lefthook", "lefthook", "lefthook.yaml")

        # Create mock resource file
        resources_dir = Path(__file__).parent.parent / "src" / "ultrapyup" / "resources"
        resources_dir.mkdir(parents=True, exist_ok=True)
        lefthook_source = resources_dir / "lefthook.yaml"
        lefthook_source.write_text("# Lefthook config")

        with patch("subprocess.run") as mock_run:
            # Simulate subprocess failure
            mock_run.side_effect = Exception("Command failed")

            with pytest.raises(Exception, match="Command failed"):
                precommit_setup("uv add", pre_commit_tool)

            # File should still be copied even if install fails
            assert (project_dir / "lefthook.yaml").exists()

    def test_setup_missing_resource_file(self, project_dir: Path):
        """Test setup when resource file doesn't exist."""
        # Use a non-existent filename to test FileNotFoundError
        pre_commit_tool = PreCommitTool(
            "NonExistent", "nonexistent", "nonexistent.yaml"
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0

            # Should raise FileNotFoundError when source file doesn't exist
            with pytest.raises(FileNotFoundError):
                precommit_setup("uv add", pre_commit_tool)


class TestPreCommitToolDataclass:
    """Tests for PreCommitTool dataclass."""

    def test_dataclass_creation(self):
        """Test creating PreCommitTool instances."""
        tool = PreCommitTool("Test Tool", "test-tool", "test.yaml")

        assert tool.name == "Test Tool"
        assert tool.value == "test-tool"
        assert tool.filename == "test.yaml"

    def test_options_list(self):
        """Test that options list contains expected pre-commit tools."""
        assert len(options) == 2

        lefthook = options[0]
        assert lefthook.name == "Lefthook"
        assert lefthook.value == "lefthook"
        assert lefthook.filename == "lefthook.yaml"

        precommit = options[1]
        assert precommit.name == "Pre-commit"
        assert precommit.value == "pre-commit"
        assert precommit.filename == ".pre-commit-config.yaml"

    def test_dataclass_equality(self):
        """Test PreCommitTool equality comparison."""
        tool1 = PreCommitTool("Test", "test", "test.yaml")
        tool2 = PreCommitTool("Test", "test", "test.yaml")
        tool3 = PreCommitTool("Different", "different", "different.yaml")

        assert tool1 == tool2
        assert tool1 != tool3
