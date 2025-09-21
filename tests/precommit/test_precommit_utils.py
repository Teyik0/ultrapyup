from unittest.mock import patch

from ultrapyup.precommit.tool import PreCommitTool
from ultrapyup.precommit.utils import get_precommit_tool


class TestGetPreCommitTools:
    """Tests for get_precommit_tool function."""

    def test_get_precommit_tool_with_provided_tools(self) -> None:
        """Test get_precommit_tool with provided tools list."""
        tool = PreCommitTool.LEFTHOOK

        with patch("ultrapyup.precommit.utils.log_selection") as mock_log:
            result = get_precommit_tool(tool)

        assert result == tool
        mock_log.assert_called_once_with(tool, "Selected pre-commit tools")

    def test_get_precommit_tool_with_none(self) -> None:
        """Test get_precommit_tool with None as input."""
        with (
            patch("ultrapyup.precommit.utils.ask") as mock_ask,
            patch("ultrapyup.precommit.utils.log_info_only") as mock_log,
        ):
            mock_ask.return_value = "Pre-commit"

            result = get_precommit_tool(None)

        expected_tool = PreCommitTool.LEFTHOOK
        assert result == expected_tool
        mock_log.assert_called_once_with(expected_tool)

    def test_get_precommit_tool_interactive_single_selection(self) -> None:
        """Test interactive selection of single precommit tool."""
        with (
            patch("ultrapyup.precommit.utils.ask") as mock_ask,
            patch("ultrapyup.precommit.utils.log_info_only") as mock_log,
        ):
            mock_ask.return_value = "Lefthook"

            result = get_precommit_tool(None)

        assert result == PreCommitTool.LEFTHOOK
        mock_log.assert_called_once_with(PreCommitTool.LEFTHOOK)

    def test_get_precommit_tool_interactive_cancel(self) -> None:
        """Test interactive selection when user cancels (ctrl+c)."""
        with (
            patch("ultrapyup.precommit.utils.ask") as mock_ask,
            patch("ultrapyup.precommit.utils.log_info_only") as mock_log,
        ):
            mock_ask.return_value = None

            result = get_precommit_tool(None)

        assert result is None
        mock_log.assert_called_once_with(None)
