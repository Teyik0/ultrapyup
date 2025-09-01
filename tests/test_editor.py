"""Tests for the editor module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ultrapyup.editor import Editor, editor_setup, get_editors, options


class TestGetEditors:
    """Tests for get_editors function."""

    def test_select_single_editor(self, capsys):
        """Test selecting a single editor."""
        with patch("ultrapyup.editor.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = ["Zed"]

            result = get_editors()

            assert result is not None
            assert len(result) == 1
            assert result[0].name == "Zed"
            assert result[0].value == "zed"
            assert result[0].file == ".rules"
            assert result[0].rule_file == ".zed"

            captured = capsys.readouterr()
            assert "zed" in captured.out

    def test_select_cursor_editor(self, capsys):
        """Test selecting Cursor editor."""
        with patch("ultrapyup.editor.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = ["Cursor"]

            result = get_editors()

            assert result is not None
            assert len(result) == 1
            assert result[0].name == "Cursor"
            assert result[0].value == "cursor"
            assert result[0].file == ""
            assert result[0].rule_file == ""

            captured = capsys.readouterr()
            assert "cursor" in captured.out

    def test_select_multiple_editors(self, capsys):
        """Test selecting multiple editors."""
        with patch("ultrapyup.editor.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = [
                "Zed",
                "GitHub Copilot (VSCode)",
                "Cursor",
            ]

            result = get_editors()

            assert result is not None
            assert len(result) == 3
            assert result[0].name == "GitHub Copilot (VSCode)"
            assert result[0].value == "vscode-copilot"
            assert result[1].name == "Cursor"
            assert result[1].value == "cursor"
            assert result[2].name == "Zed"
            assert result[2].value == "zed"

            captured = capsys.readouterr()
            assert "vscode-copilot" in captured.out
            assert "cursor" in captured.out
            assert "zed" in captured.out

    def test_select_all_editors(self, capsys):
        """Test selecting all available editors."""
        with patch("ultrapyup.editor.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = [
                "GitHub Copilot (VSCode)",
                "Cursor",
                "Windsurf",
                "Zed",
                "Claude Code",
                "OpenAI Codex",
            ]

            result = get_editors()

            assert result is not None
            assert len(result) == 6
            editor_names = [e.name for e in result]
            assert "GitHub Copilot (VSCode)" in editor_names
            assert "Cursor" in editor_names
            assert "Windsurf" in editor_names
            assert "Zed" in editor_names
            assert "Claude Code" in editor_names
            assert "OpenAI Codex" in editor_names

            captured = capsys.readouterr()
            output = captured.out
            assert "vscode-copilot" in output
            assert "cursor" in output
            assert "windsurf" in output
            assert "zed" in output
            assert "claude" in output
            assert "codex" in output

    def test_skip_selection(self, capsys):
        """Test skipping editor selection (Ctrl+C)."""
        with patch("ultrapyup.editor.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = None

            result = get_editors()

            assert result is None

            captured = capsys.readouterr()
            assert "none" in captured.out

    def test_empty_selection(self, capsys):
        """Test empty selection (no editors selected)."""
        with patch("ultrapyup.editor.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = []

            result = get_editors()

            assert result is None

            captured = capsys.readouterr()
            assert "none" in captured.out

    def test_inquirer_configuration(self):
        """Test that inquirer is configured correctly."""
        with patch("ultrapyup.editor.inquirer.select") as mock_inquirer:
            mock_select = MagicMock()
            mock_inquirer.return_value = mock_select
            mock_select.execute.return_value = []

            get_editors()

            # Verify inquirer.select was called with correct parameters
            mock_inquirer.assert_called_once()
            call_args = mock_inquirer.call_args

            assert "Which editor rules do you want to enable" in call_args[1]["message"]
            assert call_args[1]["multiselect"] is True
            assert call_args[1]["mandatory"] is False
            assert "skip" in call_args[1]["keybindings"]
            expected_choices = [
                "GitHub Copilot (VSCode)",
                "Cursor",
                "Windsurf",
                "Zed",
                "Claude Code",
                "OpenAI Codex",
            ]
            assert call_args[1]["choices"] == expected_choices


class TestEditorSetup:
    """Tests for editor_setup function."""

    def test_setup_zed_editor(self, project_dir: Path):
        """Test setting up Zed editor with both files and directories."""
        editor = Editor("Zed", "zed", ".rules", ".zed")

        # Create mock resource files and directories
        resources_dir = Path(__file__).parent.parent / "src" / "ultrapyup" / "resources"
        resources_dir.mkdir(parents=True, exist_ok=True)

        # Create .rules file
        rules_file = resources_dir / ".rules"
        rules_file.write_text("# Project rules\nRule 1\nRule 2")

        # Create .zed directory with content
        zed_dir = resources_dir / ".zed"
        zed_dir.mkdir(exist_ok=True)
        (zed_dir / "settings.json").write_text('{"theme": "dark"}')
        (zed_dir / "tasks.json").write_text('{"tasks": []}')

        editor_setup(editor)

        # Check .rules file was copied
        assert (project_dir / ".rules").exists()
        assert "# Project rules" in (project_dir / ".rules").read_text()

        # Check .zed directory was copied with contents
        assert (project_dir / ".zed").exists()
        assert (project_dir / ".zed").is_dir()
        assert (project_dir / ".zed" / "settings.json").exists()
        assert '"theme": "dark"' in (project_dir / ".zed" / "settings.json").read_text()
        assert (project_dir / ".zed" / "tasks.json").exists()
        assert '"tasks": []' in (project_dir / ".zed" / "tasks.json").read_text()

    def test_setup_editor_with_empty_files(self, project_dir: Path):
        """Test setting up editor with empty file and rule_file strings."""
        editor = Editor("Cursor", "cursor", "", "")

        # Create mock resource files
        resources_dir = Path(__file__).parent.parent / "src" / "ultrapyup" / "resources"
        resources_dir.mkdir(parents=True, exist_ok=True)

        # Create some test files in resources to verify copying behavior
        (resources_dir / "test_resource.txt").write_text("resource content")

        # When file and rule_file are empty strings, the path becomes the resources directory itself
        # This should copy the entire resources directory to the current directory
        editor_setup(editor)

        # Verify resources were copied to current directory
        assert (project_dir / "test_resource.txt").exists()
        assert "resource content" in (project_dir / "test_resource.txt").read_text()

    def test_setup_with_file_only(self, project_dir: Path):
        """Test setting up editor with file and empty rule_file."""
        editor = Editor("Test Editor", "test", ".test", "")

        # Create mock resource file
        resources_dir = Path(__file__).parent.parent / "src" / "ultrapyup" / "resources"
        resources_dir.mkdir(parents=True, exist_ok=True)
        test_file = resources_dir / ".test"
        test_file.write_text("# Test configuration")

        # Create a test file in resources to check copying behavior
        (resources_dir / "test_resource2.txt").write_text("resource2 content")

        # When rule_file is empty string, it becomes the resources directory
        # The function will copy .test file and then the entire resources directory
        editor_setup(editor)

        # Check that .test file was copied
        assert (project_dir / ".test").exists()
        assert "# Test configuration" in (project_dir / ".test").read_text()

        # Check that resources directory contents were also copied (due to empty rule_file)
        assert (project_dir / "test_resource2.txt").exists()

    def test_setup_overwrites_existing_files(self, project_dir: Path):
        """Test that setup overwrites existing editor configuration files."""
        editor = Editor("Zed", "zed", ".rules", ".zed")

        # Create existing files and directories
        existing_rules = project_dir / ".rules"
        existing_rules.write_text("# Old rules")

        existing_zed = project_dir / ".zed"
        existing_zed.mkdir()
        (existing_zed / "old_file.json").write_text('{"old": true}')

        # Create mock resource files
        resources_dir = Path(__file__).parent.parent / "src" / "ultrapyup" / "resources"
        resources_dir.mkdir(parents=True, exist_ok=True)

        rules_file = resources_dir / ".rules"
        rules_file.write_text("# New rules")

        zed_dir = resources_dir / ".zed"
        zed_dir.mkdir(exist_ok=True)
        (zed_dir / "new_file.json").write_text('{"new": true}')

        editor_setup(editor)

        # Check files were overwritten
        assert (project_dir / ".rules").exists()
        assert "# New rules" in (project_dir / ".rules").read_text()
        assert "# Old rules" not in (project_dir / ".rules").read_text()

        # Check directory was merged (dirs_exist_ok=True)
        assert (project_dir / ".zed").exists()
        assert (project_dir / ".zed" / "new_file.json").exists()
        assert '"new": true' in (project_dir / ".zed" / "new_file.json").read_text()
        # Old files should still exist due to dirs_exist_ok=True
        assert (project_dir / ".zed" / "old_file.json").exists()

    def test_setup_with_nested_directories(self, project_dir: Path):
        """Test setting up editor with nested directory structure."""
        editor = Editor("Complex Editor", "complex", ".complex", ".complex-config")

        # Create mock resource with nested directories
        resources_dir = Path(__file__).parent.parent / "src" / "ultrapyup" / "resources"
        resources_dir.mkdir(parents=True, exist_ok=True)

        # Create complex file structure
        complex_dir = resources_dir / ".complex"
        complex_dir.mkdir(exist_ok=True)
        (complex_dir / "level1").mkdir(exist_ok=True)
        (complex_dir / "level1" / "level2").mkdir(exist_ok=True)
        (complex_dir / "level1" / "file1.txt").write_text("File 1")
        (complex_dir / "level1" / "level2" / "file2.txt").write_text("File 2")

        config_dir = resources_dir / ".complex-config"
        config_dir.mkdir(exist_ok=True)
        (config_dir / "config.json").write_text('{"setting": "value"}')

        editor_setup(editor)

        # Check nested structure was copied
        assert (project_dir / ".complex").exists()
        assert (project_dir / ".complex" / "level1").exists()
        assert (project_dir / ".complex" / "level1" / "level2").exists()
        assert (project_dir / ".complex" / "level1" / "file1.txt").exists()
        assert (
            "File 1" in (project_dir / ".complex" / "level1" / "file1.txt").read_text()
        )
        assert (project_dir / ".complex" / "level1" / "level2" / "file2.txt").exists()
        assert (
            "File 2"
            in (
                project_dir / ".complex" / "level1" / "level2" / "file2.txt"
            ).read_text()
        )

        assert (project_dir / ".complex-config").exists()
        assert (project_dir / ".complex-config" / "config.json").exists()

    def test_setup_preserves_file_permissions(self, project_dir: Path):
        """Test that setup preserves source file permissions."""
        import os
        import stat

        editor = Editor("Test", "test", ".test-file", ".test-dir")

        # Create mock resources
        resources_dir = Path(__file__).parent.parent / "src" / "ultrapyup" / "resources"
        resources_dir.mkdir(parents=True, exist_ok=True)

        # Create file with specific permissions
        test_file = resources_dir / ".test-file"
        test_file.write_text("# Test file")
        os.chmod(test_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP)
        source_file_mode = test_file.stat().st_mode

        # Create directory
        test_dir = resources_dir / ".test-dir"
        test_dir.mkdir(exist_ok=True)

        editor_setup(editor)

        # Check permissions were preserved for file
        dest_file = project_dir / ".test-file"
        assert dest_file.exists()
        assert dest_file.stat().st_mode == source_file_mode

    def test_setup_missing_resource_file(self, project_dir: Path):
        """Test setup when resource file doesn't exist."""
        editor = Editor("Missing", "missing", ".missing", ".also-missing")

        # Should raise FileNotFoundError when source files don't exist
        with pytest.raises(FileNotFoundError):
            editor_setup(editor)

    def test_setup_with_symlinks(self, project_dir: Path):
        """Test that setup handles regular files (symlink test simplified to avoid resource pollution)."""
        editor = Editor("Test", "test", ".test-dir", ".test-file")

        # Create mock resources
        resources_dir = Path(__file__).parent.parent / "src" / "ultrapyup" / "resources"
        resources_dir.mkdir(parents=True, exist_ok=True)

        # Create directory with regular files
        test_dir = resources_dir / ".test-dir"
        test_dir.mkdir(exist_ok=True)
        target_file = test_dir / "target.txt"
        target_file.write_text("Target content")

        # Create regular file
        regular_file = resources_dir / ".test-file"
        regular_file.write_text("Regular file")

        editor_setup(editor)

        # Check files were copied
        assert (project_dir / ".test-dir").exists()
        assert (project_dir / ".test-dir" / "target.txt").exists()
        assert (
            "Target content" in (project_dir / ".test-dir" / "target.txt").read_text()
        )
        assert (project_dir / ".test-file").exists()
        assert "Regular file" in (project_dir / ".test-file").read_text()

        # Clean up test resources
        import shutil

        if test_dir.exists():
            shutil.rmtree(test_dir)
        if regular_file.exists():
            regular_file.unlink()


class TestEditorDataclass:
    """Tests for Editor dataclass."""

    def test_dataclass_creation(self):
        """Test creating Editor instances."""
        editor = Editor("Test Editor", "test-editor", "test.file", "test.rules")

        assert editor.name == "Test Editor"
        assert editor.value == "test-editor"
        assert editor.file == "test.file"
        assert editor.rule_file == "test.rules"

    def test_options_list(self):
        """Test that options list contains expected editors."""
        assert len(options) == 6

        # Check specific editors
        zed = next(e for e in options if e.name == "Zed")
        assert zed.value == "zed"
        assert zed.file == ".rules"
        assert zed.rule_file == ".zed"

        cursor = next(e for e in options if e.name == "Cursor")
        assert cursor.value == "cursor"
        assert cursor.file == ""
        assert cursor.rule_file == ""

        vscode = next(e for e in options if e.name == "GitHub Copilot (VSCode)")
        assert vscode.value == "vscode-copilot"
        assert vscode.file == ""
        assert vscode.rule_file == ""

        windsurf = next(e for e in options if e.name == "Windsurf")
        assert windsurf.value == "windsurf"
        assert windsurf.file == ""
        assert windsurf.rule_file == ""

        claude = next(e for e in options if e.name == "Claude Code")
        assert claude.value == "claude"
        assert claude.file == ""
        assert claude.rule_file == ""

        codex = next(e for e in options if e.name == "OpenAI Codex")
        assert codex.value == "codex"
        assert codex.file == ""
        assert codex.rule_file == ""

    def test_dataclass_equality(self):
        """Test Editor equality comparison."""
        editor1 = Editor("Test", "test", "file1", "rule1")
        editor2 = Editor("Test", "test", "file1", "rule1")
        editor3 = Editor("Different", "different", "file2", "rule2")

        assert editor1 == editor2
        assert editor1 != editor3

    def test_all_options_have_valid_values(self):
        """Test that all editor options have valid configuration."""
        for editor in options:
            assert editor.name  # Name should not be empty
            assert editor.value  # Value should not be empty
            assert isinstance(editor.file, str)  # File can be empty string
            assert isinstance(editor.rule_file, str)  # Rule file can be empty string

    def test_editor_values_are_unique(self):
        """Test that all editor values are unique."""
        values = [e.value for e in options]
        assert len(values) == len(set(values)), "Editor values should be unique"

    def test_editor_names_are_unique(self):
        """Test that all editor names are unique."""
        names = [e.name for e in options]
        assert len(names) == len(set(names)), "Editor names should be unique"
