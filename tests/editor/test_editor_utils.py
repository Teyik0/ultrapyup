from unittest.mock import patch

from ultrapyup.editor.utils import (
    EditorRule,
    EditorSetting,
    _editor_rules_ask,
    _editor_settings_ask,
    _vscode_compatible_settings,
)


class TestEditorRulesAsk:
    """Tests for _editor_rules_ask function."""

    def test_editor_rules_ask_zed_success(self) -> None:
        """Test user prompt for editor rules selection."""
        with patch("ultrapyup.editor.utils.ask") as mock_inquirer:
            mock_inquirer.return_value = [EditorRule.ZED_AI.display_name]
            result = _editor_rules_ask()

            assert result is not None
            assert len(result) == 1
            assert EditorRule.ZED_AI in result
            assert EditorRule.CLAUDE_MD not in result

    def test_editor_rules_ask_multiple_success(self) -> None:
        """Test user prompt for multiple editor rules selection."""
        with patch("ultrapyup.editor.utils.ask") as mock_inquirer:
            mock_inquirer.return_value = [
                EditorRule.ZED_AI.display_name,
                EditorRule.CURSOR_AI.display_name,
            ]
            result = _editor_rules_ask()

            assert result is not None
            assert len(result) == 2
            assert EditorRule.CURSOR_AI in result
            assert EditorRule.ZED_AI in result
            assert EditorRule.CLAUDE_MD not in result

    def test_editor_rules_ask_github_copilot_success(self) -> None:
        """Test user prompt for GitHub Copilot rule selection."""
        with patch("ultrapyup.editor.utils.ask") as mock_inquirer:
            mock_inquirer.return_value = [EditorRule.GITHUB_COPILOT.display_name]
            result = _editor_rules_ask()

            assert result is not None
            assert len(result) == 1
            assert EditorRule.GITHUB_COPILOT in result

    def test_editor_rules_ask_all_rules_success(self) -> None:
        """Test user prompt for all editor rules selection."""
        with patch("ultrapyup.editor.utils.ask") as mock_inquirer:
            mock_inquirer.return_value = [rule.display_name for rule in EditorRule]
            result = _editor_rules_ask()

            assert result is not None
            assert len(result) == len(EditorRule)
            for rule in EditorRule:
                assert rule in result

    def test_editor_rules_ask_empty_selection(self) -> None:
        """Test user prompt with empty selection (skip)."""
        with patch("ultrapyup.editor.utils.ask") as mock_inquirer:
            mock_inquirer.return_value = []
            result = _editor_rules_ask()

            assert result is None

    def test_editor_rules_ask_none_selection(self) -> None:
        """Test user prompt with None selection (Ctrl+C)."""
        with patch("ultrapyup.editor.utils.ask") as mock_inquirer:
            mock_inquirer.return_value = None
            result = _editor_rules_ask()

            assert result is None


class TestEditorSettingsAsk:
    """Tests for _editor_settings_ask function."""

    def test_editor_settings_ask_vscode_success(self) -> None:
        """Test user prompt for VSCode settings selection."""
        with patch("ultrapyup.editor.utils.ask") as mock_inquirer:
            mock_inquirer.return_value = [EditorSetting.VSCODE.display_name]
            result = _editor_settings_ask()

            assert result is not None
            assert len(result) == 1
            assert EditorSetting.VSCODE in result
            assert EditorSetting.ZED not in result

    def test_editor_settings_ask_zed_success(self) -> None:
        """Test user prompt for Zed settings selection."""
        with patch("ultrapyup.editor.utils.ask") as mock_inquirer:
            mock_inquirer.return_value = [EditorSetting.ZED.display_name]
            result = _editor_settings_ask()

            assert result is not None
            assert len(result) == 1
            assert EditorSetting.ZED in result
            assert EditorSetting.VSCODE not in result

    def test_editor_settings_ask_multiple_vscode_compatible(self) -> None:
        """Test user prompt for multiple VSCode-compatible settings (should deduplicate)."""
        with patch("ultrapyup.editor.utils.ask") as mock_inquirer:
            mock_inquirer.return_value = [
                EditorSetting.VSCODE.display_name,
                EditorSetting.CURSOR.display_name,
                EditorSetting.WINDSURF.display_name,
            ]
            result = _editor_settings_ask()

            assert result is not None
            # Should be deduplicated to only one entry since they share .vscode
            assert len(result) == 1
            assert result[0].settings_dir == ".vscode"

    def test_editor_settings_ask_different_settings_dirs(self) -> None:
        """Test user prompt for settings with different directories."""
        with patch("ultrapyup.editor.utils.ask") as mock_inquirer:
            mock_inquirer.return_value = [
                EditorSetting.VSCODE.display_name,
                EditorSetting.ZED.display_name,
            ]
            result = _editor_settings_ask()

            assert result is not None
            assert len(result) == 2

            # Check that we have both VSCode and Zed settings
            settings_dirs = {s.settings_dir for s in result}
            assert ".vscode" in settings_dirs
            assert ".zed" in settings_dirs

    def test_editor_settings_ask_all_settings_success(self) -> None:
        """Test user prompt for all editor settings selection."""
        with patch("ultrapyup.editor.utils.ask") as mock_inquirer:
            mock_inquirer.return_value = [setting.display_name for setting in EditorSetting]
            result = _editor_settings_ask()

            assert result is not None
            # Should be deduplicated (VSCode-compatible editors share same dir)
            assert len(result) == 3  # .vscode and .zed
            settings_dirs = {s.settings_dir for s in result}
            assert ".vscode" in settings_dirs
            assert ".zed" in settings_dirs

    def test_editor_settings_ask_empty_selection(self) -> None:
        """Test user prompt with empty selection (skip)."""
        with patch("ultrapyup.editor.utils.ask") as mock_ask:
            mock_ask.return_value = []
            result = _editor_settings_ask()

            assert result is None

    def test_editor_settings_ask_none_selection(self) -> None:
        """Test user prompt with None selection (Ctrl+C)."""
        with patch("ultrapyup.editor.utils.ask") as mock_ask:
            mock_ask.return_value = None
            result = _editor_settings_ask()

            assert result is None


class TestVSCodeCompatibleSettings:
    """Tests for _vscode_compatible_settings function."""

    def test_vscode_compatible_settings_single_setting(self) -> None:
        """Test deduplication with single setting."""
        settings = [EditorSetting.VSCODE]
        result = _vscode_compatible_settings(settings)

        assert len(result) == 1
        assert EditorSetting.VSCODE in result

    def test_vscode_compatible_settings_multiple_vscode_compatible(self) -> None:
        """Test deduplication with multiple VSCode-compatible settings."""
        settings = [EditorSetting.VSCODE, EditorSetting.CURSOR, EditorSetting.WINDSURF, EditorSetting.KIRO]
        result = _vscode_compatible_settings(settings)

        # Should be deduplicated to only one entry since they share .vscode
        assert len(result) == 1
        assert result[0].settings_dir == ".vscode"
        # Should be the first one in the list
        assert result[0] == EditorSetting.VSCODE

    def test_vscode_compatible_settings_mixed_settings(self) -> None:
        """Test deduplication with mixed settings directories."""
        settings = [EditorSetting.VSCODE, EditorSetting.CURSOR, EditorSetting.ZED]
        result = _vscode_compatible_settings(settings)

        # Should have 2 entries: one for .vscode, one for .zed
        assert len(result) == 2
        settings_dirs = {s.settings_dir for s in result}
        assert ".vscode" in settings_dirs
        assert ".zed" in settings_dirs

    def test_vscode_compatible_settings_zed_only(self) -> None:
        """Test deduplication with only Zed setting."""
        settings = [EditorSetting.ZED]
        result = _vscode_compatible_settings(settings)

        assert len(result) == 1
        assert EditorSetting.ZED in result

    def test_vscode_compatible_settings_empty_list(self) -> None:
        """Test deduplication with empty list."""
        settings = []
        result = _vscode_compatible_settings(settings)

        assert len(result) == 0
        assert result == []

    def test_vscode_compatible_settings_preserves_order(self) -> None:
        """Test that deduplication preserves the order of first occurrence."""
        settings = [EditorSetting.CURSOR, EditorSetting.VSCODE, EditorSetting.WINDSURF]
        result = _vscode_compatible_settings(settings)

        # Should be deduplicated to only one entry, and it should be CURSOR (first in list)
        assert len(result) == 1
        assert result[0] == EditorSetting.CURSOR
