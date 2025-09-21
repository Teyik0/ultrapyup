from ultrapyup.precommit.tool import PreCommitTool
from ultrapyup.utils import ask, log


precommit_tools = [tool for tool in PreCommitTool if tool != PreCommitTool.SKIP]


def _precommit_tools_ask() -> PreCommitTool | None:
    """Prompt user to select pre-commit tools interactively.

    Returns:
        List of selected PreCommitTool objects.
    """
    value = ask(
        msg="Which pre-commit tool would you like to use ? (optional - skip with ctrl+c)",
        choices=[tool.display_name for tool in precommit_tools],
        multiselect=False,
    )

    if not value:
        return None

    for tool in precommit_tools:
        if tool.display_name == value:
            return tool
    raise ValueError(f"Unknown precommit tool: {value}")


def get_precommit_tool(precommit_tool: PreCommitTool | None = None) -> PreCommitTool | None:
    """Get the selected pre-commit tools from user input or parameter.

    Args:
        precommit_tool: Pre-commit tools to use (optional)

    Returns:
        PreCommitTool object, or None if no tool was selected.
    """
    # Ask user for tools
    if precommit_tool is None:
        tool = _precommit_tools_ask()
        log.info(tool.value if tool else "none")
        return tool

    # Handle explicit skip
    if precommit_tool.value == "skip":
        log.title("Selected pre-commit tool")
        log.info("none")
        return None

    # Handle explicit tools provided
    log.title("Selected pre-commit tool")
    log.info(precommit_tool.value)
    return precommit_tool
