from unittest.mock import patch

import pytest

from ultrapyup.pre_commit import (
    get_precommit_tool,
)


class TestGetPrecommitTool:
    """Tests for get_precommit_tool function."""

    def test_select_lefthook(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test selecting Lefthook as pre-commit tool."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = ["Lefthook"]
            result = get_precommit_tool()

            assert result is not None
            assert len(result) == 1
            assert result[0].name == "Lefthook"
            assert result[0].value == "lefthook"
            assert result[0].filename == "lefthook.yaml"

            captured = capsys.readouterr()
            assert "lefthook" in captured.out

    def test_select_precommit(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test selecting Pre-commit as pre-commit tool."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = ["Pre-commit"]
            result = get_precommit_tool()

            assert result is not None
            assert len(result) == 1
            assert result[0].name == "Pre-commit"
            assert result[0].value == "pre-commit"
            assert result[0].filename == ".pre-commit-config.yaml"

            captured = capsys.readouterr()
            assert "pre-commit" in captured.out

    def test_select_multiple_tools(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test selecting multiple pre-commit tools."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = ["Lefthook", "Pre-commit"]
            result = get_precommit_tool()

            assert result is not None
            assert len(result) == 2
            assert result[0].name == "Lefthook"
            assert result[1].name == "Pre-commit"

            captured = capsys.readouterr()
            assert "lefthook" in captured.out
            assert "pre-commit" in captured.out

    def test_skip_selection(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test skipping pre-commit tool selection (Ctrl+C)."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = None
            result = get_precommit_tool()

            assert result is None

            captured = capsys.readouterr()
            assert "none" in captured.out

    def test_empty_selection(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test empty selection (no tools selected)."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = []
            result = get_precommit_tool()

            assert result is None

            captured = capsys.readouterr()
            assert "none" in captured.out

    def test_inquirer_configuration(self) -> None:
        """Test that inquirer is configured correctly."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = []
            get_precommit_tool()

            # Verify inquirer.select was called with correct parameters
            mock_inquirer.assert_called_once()
            call_args = mock_inquirer.call_args

            assert "Which pre-commit tool would you like to use" in call_args[1]["message"]
            assert call_args[1]["multiselect"] is True
            assert call_args[1]["mandatory"] is False
            assert "skip" in call_args[1]["keybindings"]
            assert call_args[1]["choices"] == ["Lefthook", "Pre-commit"]
