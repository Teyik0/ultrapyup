from ultrapyup.precommit.tool import PreCommitTool
from ultrapyup.utils import ask, log_info_only, log_selection


def _precommit_tools_ask() -> list[PreCommitTool] | None:
    """Prompt user to select pre-commit tools interactively.

    Returns:
        List of selected PreCommitTool objects.
    """
    values = ask(
        msg="Which pre-commit tool would you like to use ? (optional - skip with ctrl+c)",
        choices=[tool.display_name for tool in PreCommitTool],
        multiselect=True,
    )

    if not values or any(value == "skip" for value in values):
        return None

    selected_tools = [tool for tool in PreCommitTool if tool.display_name in values]
    return selected_tools


def get_precommit_tools(precommit_tools: list[PreCommitTool] | None = None) -> list[PreCommitTool] | None:
    """Get the selected pre-commit tools from user input or parameter.

    Args:
        precommit_tools: List of pre-commit tools to use (optional)

    Returns:
        List of selected PreCommitTool objects, or None if no tools were selected.
    """
    # Ask user for tools
    if precommit_tools is None:
        tools = _precommit_tools_ask()
        log_info_only(tools)
        return tools

    # Handle explicit skip
    if any(precommit_tool.value == "skip" for precommit_tool in precommit_tools):
        log_selection(None, "Selected pre-commit tools")
        return None

    # Handle explicit tools provided
    log_selection(precommit_tools, "Selected pre-commit tools")
    return precommit_tools
