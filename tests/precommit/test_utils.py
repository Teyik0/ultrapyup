from unittest.mock import patch

from ultrapyup.precommit.tool import PreCommitTool
from ultrapyup.precommit.utils import get_precommit_tools


class TestGetPreCommitTools:
    """Tests for get_precommit_tools function."""

    def test_get_precommit_tools_with_provided_tools(self) -> None:
        """Test get_precommit_tools with provided tools list."""
        tools = [PreCommitTool.LEFTHOOK, PreCommitTool.PRE_COMMIT]

        with patch("ultrapyup.precommit.utils.log") as mock_log:
            result = get_precommit_tools(tools)

        assert result == tools
        mock_log.info.assert_called_once_with("lefthook, pre-commit")

    def test_get_precommit_tools_with_empty_list(self) -> None:
        """Test get_precommit_tools with empty tools list."""
        tools = []

        with patch("ultrapyup.precommit.utils.log") as mock_log:
            result = get_precommit_tools(tools)

        assert result is None
        mock_log.info.assert_called_once_with("none")

    def test_get_precommit_tools_with_none(self) -> None:
        """Test get_precommit_tools with None as input."""
        with (
            patch("ultrapyup.precommit.utils.inquirer") as mock_inquirer,
            patch("ultrapyup.precommit.utils.log") as mock_log,
        ):
            mock_inquirer.select.return_value.execute.return_value = ["Lefthook", "Pre-commit"]

            result = get_precommit_tools(None)

        expected_tools = [PreCommitTool.LEFTHOOK, PreCommitTool.PRE_COMMIT]
        assert result == expected_tools
        mock_log.info.assert_called_once_with("lefthook, pre-commit")

    def test_get_precommit_tools_interactive_single_selection(self) -> None:
        """Test interactive selection of single precommit tool."""
        with (
            patch("ultrapyup.precommit.utils.inquirer") as mock_inquirer,
            patch("ultrapyup.precommit.utils.log") as mock_log,
        ):
            mock_inquirer.select.return_value.execute.return_value = ["Lefthook"]

            result = get_precommit_tools(None)

        assert result == [PreCommitTool.LEFTHOOK]
        mock_log.info.assert_called_once_with("lefthook")

    def test_get_precommit_tools_interactive_no_selection(self) -> None:
        """Test interactive selection with no tools selected."""
        with (
            patch("ultrapyup.precommit.utils.inquirer") as mock_inquirer,
            patch("ultrapyup.precommit.utils.log") as mock_log,
        ):
            mock_inquirer.select.return_value.execute.return_value = []

            result = get_precommit_tools(None)

        assert result is None
        mock_log.info.assert_called_once_with("none")

    def test_get_precommit_tools_interactive_cancel(self) -> None:
        """Test interactive selection when user cancels (ctrl+c)."""
        with (
            patch("ultrapyup.precommit.utils.inquirer") as mock_inquirer,
            patch("ultrapyup.precommit.utils.log") as mock_log,
        ):
            mock_inquirer.select.return_value.execute.return_value = None

            result = get_precommit_tools(None)

        assert result is None
        mock_log.info.assert_called_once_with("none")
