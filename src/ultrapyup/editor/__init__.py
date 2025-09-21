from ultrapyup.editor.rule import EditorRule
from ultrapyup.editor.setting import EditorSetting
from ultrapyup.editor.utils import (
    _editor_rules_ask,
    _editor_settings_ask,
    _vscode_compatible_settings,
    rule_options,
    setting_options,
)
from ultrapyup.utils import log_info_only, log_selection


def get_editor_rules(editor_rules: list[EditorRule] | None = None) -> list[EditorRule] | None:
    """Get user-selected AI rules through interactive prompt or parameter."""
    # Ask user for rules
    if editor_rules is None:
        rules = _editor_rules_ask()
        log_info_only(rules)
        return rules

    # Handle explicit skip
    if any(rule.value == "skip" for rule in editor_rules):
        log_selection(None, "Selected AI rules")
        return None

    # Handle explicit rules provided
    log_selection(editor_rules, "Selected AI rules")
    return editor_rules


def get_editor_settings(
    editor_settings: list[EditorSetting] | None = None,
) -> list[EditorSetting] | None:
    """Get user-selected editor settings through interactive prompt or parameter."""
    # Ask user for settings
    if editor_settings is None:
        settings = _editor_settings_ask()
        log_info_only(settings)
        return settings

    # Handle explicit skip
    if any(setting.value == "skip" for setting in editor_settings):
        log_selection(None, "Selected editor settings")
        return None

    # Handle explicit settings provided
    settings = _vscode_compatible_settings(editor_settings)
    log_selection(settings, "Selected editor settings")
    return settings


__all__ = [
    "EditorRule",
    "EditorSetting",
    "rule_options",
    "setting_options",
]
