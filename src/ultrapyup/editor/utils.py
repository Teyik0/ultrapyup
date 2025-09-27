from ultrapyup.editor.rule import EditorRule
from ultrapyup.editor.setting import EditorSetting
from ultrapyup.utils import ask


rule_options: list[EditorRule] = [rule for rule in EditorRule if rule != EditorRule.SKIP]
setting_options: list[EditorSetting] = [setting for setting in EditorSetting if setting != EditorSetting.SKIP]


def _editor_rules_ask() -> list[EditorRule] | None:
    selected_rules = ask(
        msg="Which AI rules do you want to enable? (optional - skip with ctrl+c)",
        choices=[rule.display_name for rule in rule_options],
        multiselect=True,
    )

    if not selected_rules:
        return None

    rules: list[EditorRule] = [rule for rule in rule_options if rule.display_name in selected_rules]
    return rules


def _editor_settings_ask() -> list[EditorSetting] | None:
    values = ask(
        msg="Which editor settings do you want to configure? (optional - skip with ctrl+c)",
        choices=[settings.display_name for settings in setting_options],
        multiselect=True,
    )

    if not values:
        return None

    settings: list[EditorSetting] = [setting for setting in setting_options if setting.display_name in values]
    return _vscode_compatible_settings(settings)


def _vscode_compatible_settings(settings: list[EditorSetting]) -> list[EditorSetting]:
    """Deduplicate VSCode-compatible settings."""
    unique_dirs = {setting.settings_dir for setting in settings}
    unique_settings = []
    for dir_name in unique_dirs:
        # Get the first setting with this directory
        for setting in settings:
            if setting.settings_dir == dir_name:
                unique_settings.append(setting)
                break
    return unique_settings
