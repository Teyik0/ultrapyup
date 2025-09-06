import shutil
from dataclasses import dataclass
from pathlib import Path

from InquirerPy import inquirer

from ultrapyup.utils import log


@dataclass
class EditorRule:
    """Configuration for AI rules/instructions for code editors."""

    name: str
    value: str
    target_file: str  # The file name to create in the project
    source_file: str = ".rules"  # Source file from resources (default: .rules)


@dataclass
class EditorSetting:
    """Configuration for editor settings and extensions."""

    name: str
    value: str
    settings_dir: str  # Directory containing settings (e.g., .vscode)


rule_options = [
    EditorRule(
        name="GitHub Copilot",
        value="github-copilot",
        target_file=".github/copilot-instructions.md",
    ),
    EditorRule(
        name="Cursor AI",
        value="cursor-ai",
        target_file=".cursorrules",
    ),
    EditorRule(
        name="Windsurf AI",
        value="windsurf-ai",
        target_file=".windsurfrules",
    ),
    EditorRule(
        name="Claude (CLAUDE.md)",
        value="claude-md",
        target_file="CLAUDE.md",
    ),
    EditorRule(
        name="Zed AI",
        value="zed-ai",
        target_file=".rules",
        source_file=".rules",
    ),
]

setting_options = [
    EditorSetting(
        name="VSCode",
        value="vscode",
        settings_dir=".vscode",
    ),
    EditorSetting(
        name="Cursor",
        value="cursor",
        settings_dir=".vscode",
    ),
    EditorSetting(
        name="Windsurf",
        value="windsurf",
        settings_dir=".vscode",
    ),
    EditorSetting(
        name="Kiro",
        value="kiro",
        settings_dir=".vscode",
    ),
    EditorSetting(
        name="Zed",
        value="zed",
        settings_dir=".zed",
    ),
]


def get_editors_rules() -> list[EditorRule] | None:
    """Get user-selected AI rules through interactive prompt.

    Returns:
        List of selected EditorRule objects, or None if no rules were selected.
    """
    values = inquirer.select(
        message="Which AI rules do you want to enable? (optional - skip with ctrl+c)",
        choices=[rule.name for rule in rule_options],
        multiselect=True,
        qmark="◆ ",
        amark="◇ ",
        pointer="◼ ",
        marker="◻ ",
        marker_pl=" ",
        transformer=lambda _: "",
        keybindings={
            "skip": [{"key": "c-c"}],
        },
        mandatory=False,
    ).execute()

    if not values:
        log.info("none")
        return None

    rules: list[EditorRule] = [rule for rule in rule_options if rule.name in values]

    log.info(", ".join(rule.value for rule in rules))
    return rules


def get_editors_settings() -> list[EditorSetting] | None:
    """Get user-selected editor settings through interactive prompt.

    Returns:
        List of selected EditorSetting objects, or None if no settings were selected.
    """
    values = inquirer.select(
        message=("Which editor settings do you want to configure? (optional - skip with ctrl+c)"),
        choices=[setting.name for setting in setting_options],
        multiselect=True,
        qmark="◆ ",
        amark="◇ ",
        pointer="◼ ",
        marker="◻ ",
        marker_pl=" ",
        transformer=lambda _: "",
        keybindings={
            "skip": [{"key": "c-c"}],
        },
        mandatory=False,
    ).execute()

    if not values:
        log.info("none")
        return None

    settings: list[EditorSetting] = [setting for setting in setting_options if setting.name in values]

    # Deduplicate VSCode-compatible settings
    unique_dirs = {setting.settings_dir for setting in settings}
    unique_settings = []
    for dir_name in unique_dirs:
        # Get the first setting with this directory
        for setting in settings:
            if setting.settings_dir == dir_name:
                unique_settings.append(setting)
                break

    log.info(", ".join(setting.value for setting in settings))
    return unique_settings


def editor_rule_setup(rule: EditorRule) -> None:
    """Set up AI rule files by copying and renaming them.

    Args:
        rule: EditorRule configuration containing file paths.
    """
    current_file = Path(__file__)
    source_file = current_file.parent / "resources" / rule.source_file
    target_path = Path.cwd() / rule.target_file

    # Create parent directory if needed
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Copy the source file to the target location
    if source_file.is_file():
        shutil.copy2(source_file, target_path)
    else:
        raise FileNotFoundError(f"Source file {source_file} not found")


def editor_settings_setup(setting: EditorSetting) -> None:
    """Set up editor settings by copying configuration directories.

    Args:
        setting: EditorSetting configuration containing directory paths.
    """
    current_file = Path(__file__)
    source_dir = current_file.parent / "resources" / setting.settings_dir
    target_dir = Path.cwd() / setting.settings_dir

    shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
