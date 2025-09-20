from ultrapyup.config import ruff_config_setup, ty_config_setup
from ultrapyup.editor import (
    EditorRule,
    EditorSetting,
    get_editor_rules,
    get_editor_settings,
)
from ultrapyup.layout import detect_project_layout
from ultrapyup.migrate import _check_python_project, _migrate_requirements_to_pyproject
from ultrapyup.package_manager import PackageManager, get_package_manager, install_dependencies
from ultrapyup.precommit import PreCommitTool, get_precommit_tools
from ultrapyup.utils import log


def initialize(
    package_manager: PackageManager | None = None,
    editor_rules: list[EditorRule] | None = None,
    editor_settings: list[EditorSetting] | None = None,
    precommit_tools: list[PreCommitTool] | None = None,
) -> None:
    """Initialize and configure a Python project with development tools.

    Args:
        package_manager: Package manager to use
        editor_rules: List of AI rules to enable
        editor_settings: List of editor settings to configure
        precommit_tools: List of pre-commit tools to use
    """
    if not _check_python_project():
        raise RuntimeError("Not a Python project (no pyproject.toml or setup.py found)")

    _migrate_requirements_to_pyproject()
    selected_package_manager = get_package_manager(package_manager)
    selected_editor_rules = get_editor_rules(editor_rules)
    selected_editor_settings = get_editor_settings(editor_settings)
    selected_pre_commit_tools = get_precommit_tools(precommit_tools)

    # Configure user's experience
    install_dependencies(selected_package_manager, selected_pre_commit_tools)
    ruff_config_setup()
    ty_config_setup(detect_project_layout())

    if selected_pre_commit_tools:
        for tool in selected_pre_commit_tools:
            tool.setup(selected_package_manager)
        log.title("Pre-commit setup completed")
        log.info(f"{', '.join(tool.filename for tool in selected_pre_commit_tools)} created")

    if selected_editor_rules:
        for rule in selected_editor_rules:
            rule.setup(selected_package_manager)
        log.title("AI rules setup completed")
        log.info(f"{', '.join(rule.target_file for rule in selected_editor_rules)} created")

    if selected_editor_settings:
        for setting in selected_editor_settings:
            setting.setup()
        log.title("Editor settings setup completed")
        log.info(f"{', '.join(setting.settings_dir for setting in selected_editor_settings)} created")
