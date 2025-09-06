from ultrapyup.editor import (
    editor_rule_setup,
    editor_settings_setup,
    get_editors_rules,
    get_editors_settings,
)
from ultrapyup.migrate import _check_python_project, _migrate_requirements_to_pyproject
from ultrapyup.package_manager import (
    get_package_manager,
    install_dependencies,
    ruff_config_setup,
    ty_config_setup,
)
from ultrapyup.pre_commit import get_precommit_tool, precommit_setup
from ultrapyup.utils import log


def initialize() -> None:
    """Initialize and configure a Python project with development tools."""
    if not _check_python_project():
        return

    # Migrate requirements.txt to pyproject.toml if needed
    _migrate_requirements_to_pyproject()

    # Ask user's preferences
    package_manager = get_package_manager()
    editor_rules = get_editors_rules()
    editor_settings = get_editors_settings()
    pre_commit_tools = get_precommit_tool()

    # Configure user's experience
    install_dependencies(package_manager, pre_commit_tools)
    ruff_config_setup()
    ty_config_setup()

    if pre_commit_tools:
        for tool in pre_commit_tools:
            precommit_setup(package_manager, tool)
        log.title("Pre-commit setup completed")
        log.info(f"{', '.join(tool.filename for tool in pre_commit_tools)} created")

    if editor_rules:
        for rule in editor_rules:
            editor_rule_setup(rule)
        log.title("AI rules setup completed")
        log.info(f"{', '.join(rule.target_file for rule in editor_rules)} created")

    if editor_settings:
        for setting in editor_settings:
            editor_settings_setup(setting)
        log.title("Editor settings setup completed")
        log.info(f"{', '.join(setting.settings_dir for setting in editor_settings)} created")

    return
