from ultrapyup.editor.rule import EditorRule
from ultrapyup.editor.setting import EditorSetting
from ultrapyup.editor.utils import (
    _editor_rules_ask,
    _editor_settings_ask,
    _vscode_compatible_settings,
    setting_options,
)
from ultrapyup.utils import log


def get_editors_rules(editor_rules: list[EditorRule] | None = None) -> list[EditorRule] | None:
    """Get user-selected AI rules through interactive prompt or parameter.

    Args:
        editor_rules: List of editor rule values to enable (optional)

    Returns:
        List of selected EditorRule objects, or None if no rules were selected.
    """
    if editor_rules is None:
        rules = _editor_rules_ask()
    elif len(editor_rules) > 0:
        rules = editor_rules
    else:  # Empty list, user explicitly wants no rules --editor-rules
        rules = None

    if not rules:
        log.info("none")
        return None
    else:
        log.info(", ".join(rule.value for rule in rules))
        return rules


def get_editors_settings(editor_settings: list[EditorSetting] | None = None) -> list[EditorSetting] | None:
    """Get user-selected editor settings through interactive prompt or parameter.

    Args:
        editor_settings: List of editor setting values to configure (optional)

    Returns:
        List of selected EditorSetting objects, or None if no settings were selected.
    """
    if editor_settings is None:
        settings = _editor_settings_ask()
    elif len(editor_settings) > 0:
        settings = _vscode_compatible_settings(editor_settings)
    else:  # Empty list, user explicitly wants no rules --editor-rules
        settings = None

    if not settings:
        log.info("none")
        return None
    else:
        log.info(", ".join(rule.value for rule in settings))
        return settings


__all__ = [
    "EditorRule",
    "EditorSetting",
    "rule_options",
    "setting_options",
]
