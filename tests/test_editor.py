"""Tests for the editor module."""

from unittest.mock import MagicMock, patch

from ultrapyup.editor import get_editors


class TestGetEditors:
    """Tests for get_editors function."""

    def test_select_single_editor(self, capsys):
        """Test selecting a single editor."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
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
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
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
