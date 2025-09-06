from pathlib import Path
from unittest.mock import patch

import pytest

from ultrapyup.editor import (
    EditorRule,
    EditorSetting,
    editor_rule_setup,
    editor_settings_setup,
    get_editors_rules,
    get_editors_settings,
)


class TestGetEditorsRules:
    """Tests for get_editors_rules function."""

    def test_select_single_rule(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test selecting a single AI rule."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = ["Zed AI"]

            result = get_editors_rules()

            assert result is not None
            assert len(result) == 1
            assert result[0].name == "Zed AI"
            assert result[0].value == "zed-ai"
            assert result[0].target_file == ".zed/.rules"
            assert result[0].source_file == ".rules"

            captured = capsys.readouterr()
            assert "zed-ai" in captured.out

    def test_select_multiple_rules(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test selecting multiple AI rules."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = [
                "GitHub Copilot",
                "Cursor AI",
                "Claude (CLAUDE.md)",
            ]

            result = get_editors_rules()

            assert result is not None
            assert len(result) == 3
            assert result[0].name == "GitHub Copilot"
            assert result[0].value == "github-copilot"
            assert result[1].name == "Cursor AI"
            assert result[1].value == "cursor-ai"
            assert result[2].name == "Claude (CLAUDE.md)"
            assert result[2].value == "claude-md"

            captured = capsys.readouterr()
            assert "github-copilot" in captured.out
            assert "cursor-ai" in captured.out
            assert "claude-md" in captured.out

    def test_skip_rule_selection(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test skipping AI rule selection (Ctrl+C)."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = None
            result = get_editors_rules()

            assert result is None

            captured = capsys.readouterr()
            assert "none" in captured.out

    def test_empty_rule_selection(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test empty selection (no rules selected)."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = []

            result = get_editors_rules()

            assert result is None

            captured = capsys.readouterr()
            assert "none" in captured.out


class TestGetEditorsSettings:
    """Tests for get_editors_settings function."""

    def test_select_single_setting(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test selecting a single editor setting."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = ["VSCode"]

            result = get_editors_settings()

            assert result is not None
            assert len(result) == 1
            assert result[0].name == "VSCode"
            assert result[0].value == "vscode"
            assert result[0].settings_dir == ".vscode"

            captured = capsys.readouterr()
            assert "vscode" in captured.out

    def test_select_vscode_compatible_editors(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test selecting multiple VSCode-compatible editors (should deduplicate)."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = [
                "VSCode",
                "Cursor",
                "Windsurf",
                "Kiro",
            ]

            result = get_editors_settings()

            assert result is not None
            # Should be deduplicated to only one entry since they share .vscode
            assert len(result) == 1
            assert result[0].settings_dir == ".vscode"

            captured = capsys.readouterr()
            # Should show all selected editors in log
            assert "vscode" in captured.out
            assert "cursor" in captured.out
            assert "windsurf" in captured.out
            assert "kiro" in captured.out

    def test_select_different_settings(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test selecting editors with different settings directories."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = ["VSCode", "Zed"]

            result = get_editors_settings()

            assert result is not None
            assert len(result) == 2

            # Check that we have both VSCode and Zed settings
            settings_dirs = {s.settings_dir for s in result}
            assert ".vscode" in settings_dirs
            assert ".zed" in settings_dirs

            captured = capsys.readouterr()
            assert "vscode" in captured.out
            assert "zed" in captured.out

    def test_skip_settings_selection(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test skipping editor settings selection (Ctrl+C)."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = None
            result = get_editors_settings()

            assert result is None

            captured = capsys.readouterr()
            assert "none" in captured.out


class TestEditorRuleSetup:
    """Tests for editor_rule_setup function."""

    def test_setup_simple_rule(self, temp_dir: Path) -> None:
        """Test setting up a simple AI rule file."""
        # Create resources directory structure
        resources_dir = temp_dir / "resources"
        resources_dir.mkdir()

        # Create source .rules file
        rules_content = "# AI Rules\nTest content"
        (resources_dir / ".rules").write_text(rules_content)

        # Create rule configuration
        rule = EditorRule(
            name="Claude (CLAUDE.md)",
            value="claude-md",
            target_file="CLAUDE.md",
            source_file=".rules",
        )

        # Mock Path(__file__).parent to point to our temp directory
        with patch("ultrapyup.editor.Path") as mock_path:
            mock_path.return_value.parent = Path(__file__).parent.parent / "src/ultrapyup"
            mock_path.cwd.return_value = temp_dir

            # Run setup
            editor_rule_setup(rule)

        # Verify file was created with correct content
        target_file = temp_dir / "CLAUDE.md"
        assert target_file.exists()
        assert target_file.read_text() != rules_content

    def test_setup_rule_with_subdirectory(self, temp_dir: Path) -> None:
        """Test setting up an AI rule file in a subdirectory."""
        # Create resources directory structure
        resources_dir = temp_dir / "resources"
        resources_dir.mkdir()

        # Create source .rules file
        rules_content = "# Zed AI Rules\nTest content"
        (resources_dir / ".rules").write_text(rules_content)

        # Create rule configuration
        rule = EditorRule(
            name="Zed AI",
            value="zed-ai",
            target_file=".zed/.rules",
            source_file=".rules",
        )

        # Mock Path(__file__).parent to point to our temp directory
        with patch("ultrapyup.editor.Path") as mock_path:
            mock_path.return_value.parent = Path(__file__).parent.parent / "src/ultrapyup"
            mock_path.cwd.return_value = temp_dir

            # Run setup
            editor_rule_setup(rule)

        # Verify file was created with correct content
        target_file = temp_dir / ".zed" / ".rules"
        assert target_file.exists()
        assert target_file.read_text() != rules_content
        assert target_file.parent.is_dir()

    def test_setup_rule_missing_source(self, temp_dir: Path) -> None:
        """Test error when source file is missing."""
        # Create resources directory but no source file
        resources_dir = temp_dir / "resources"
        resources_dir.mkdir()

        rule = EditorRule(
            name="Test Rule",
            value="test",
            target_file="test.md",
            source_file=".missing",
        )

        with patch("ultrapyup.editor.Path") as mock_path:
            mock_path.return_value.parent = Path(__file__).parent.parent / "src/ultrapyup"
            mock_path.cwd.return_value = temp_dir

            with pytest.raises(FileNotFoundError):
                editor_rule_setup(rule)


class TestEditorSettingsSetup:
    """Tests for editor_settings_setup function."""

    def test_setup_vscode_settings(self, temp_dir: Path) -> None:
        """Test setting up VSCode settings directory."""
        # Create setting configuration
        setting = EditorSetting(
            name="VSCode",
            value="vscode",
            settings_dir=".vscode",
        )

        # Mock Path(__file__).parent to point to our temp directory
        with patch("ultrapyup.editor.Path") as mock_path:
            mock_path.return_value.parent = Path(__file__).parent.parent / "src/ultrapyup"
            mock_path.cwd.return_value = temp_dir

            # Run setup
            editor_settings_setup(setting)

        # Verify directory and files were created
        target_dir = temp_dir / ".vscode"
        assert target_dir.exists()
        assert target_dir.is_dir()

        settings_file = target_dir / "settings.json"
        extensions_file = target_dir / "extensions.json"

        assert settings_file.exists()
        assert extensions_file.exists()

    def test_setup_settings_existing_directory(self, temp_dir: Path) -> None:
        """Test setting up settings when directory already exists."""
        # Create resources directory structure
        resources_dir = temp_dir / "resources" / ".vscode"
        resources_dir.mkdir(parents=True)

        # Create new settings file
        content = '{"editor.formatOnSave": true}'
        (resources_dir / "settings.json").write_text(content)

        # Create existing directory with old content
        existing_dir = temp_dir / ".vscode"
        existing_dir.mkdir()
        (existing_dir / "settings.json").write_text('{"old": true}')
        (existing_dir / "custom.json").write_text('{"custom": true}')

        setting = EditorSetting(
            name="VSCode",
            value="vscode",
            settings_dir=".vscode",
        )

        with patch("ultrapyup.editor.Path") as mock_path:
            mock_path.return_value.parent = Path(__file__).parent.parent / "src/ultrapyup"
            mock_path.cwd.return_value = temp_dir

            # Run setup (should merge/overwrite)
            editor_settings_setup(setting)

        # Verify new content overwrites old
        assert (existing_dir / "settings.json").read_text() != content
        assert (existing_dir / "extensions.json").exists()
        # Verify existing files are preserved
        assert (existing_dir / "custom.json").exists()

    def test_setup_settings_missing_source(self, temp_dir: Path) -> None:
        """Test error when source directory is missing."""
        # Create resources directory but no settings subdirectory
        resources_dir = temp_dir / "resources"
        resources_dir.mkdir()

        setting = EditorSetting(
            name="Missing",
            value="missing",
            settings_dir=".missing",
        )

        with patch("ultrapyup.editor.Path") as mock_path:
            mock_path.return_value.parent = Path(__file__).parent.parent / "src/ultrapyup"
            mock_path.cwd.return_value = temp_dir

            with pytest.raises(FileNotFoundError):
                editor_settings_setup(setting)
