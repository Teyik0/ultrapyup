import shutil
from dataclasses import dataclass
from pathlib import Path

from InquirerPy import inquirer

from ultrapyup.utils import log


@dataclass
class Editor:
    """Configuration for a code editor with associated rule files."""

    name: str
    value: str
    file: str
    rule_file: str


options = [
    Editor(
        name="GitHub Copilot (VSCode)",
        value="vscode-copilot",
        file="",
        rule_file="",
    ),
    Editor(name="Cursor", value="cursor", file="", rule_file=""),
    Editor(name="Windsurf", value="windsurf", file="", rule_file=""),
    Editor(name="Zed", value="zed", file=".rules", rule_file=".zed"),
    Editor(name="Claude Code", value="claude", file="", rule_file=""),
    Editor(name="OpenAI Codex", value="codex", file="", rule_file=""),
]


def get_editors() -> list[Editor] | None:
    """Get user-selected editors through interactive prompt.

    Returns:
        List of selected Editor objects, or None if no editors were selected.
    """
    values = inquirer.select(
        message="Which editor rules do you want to enable ? (optional - skip with ctrl+c)",
        choices=[editor.name for editor in options],
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

    editors: list[Editor] = [editor for editor in options if editor.name in values]

    log.info(", ".join(editor.value for editor in editors))
    return editors


def editor_setup(editor: Editor) -> None:
    """Set up editor configuration files by copying them to the current working directory.

    Args:
        editor: Editor configuration containing file paths and settings.
    """
    current_file = Path(__file__)
    editor_file = current_file.parent / "resources" / editor.file
    editor_rule_file = current_file.parent / "resources" / editor.rule_file

    if editor_file.is_dir():
        shutil.copytree(editor_file, Path.cwd() / editor.file, dirs_exist_ok=True)
    else:
        shutil.copy2(editor_file, Path.cwd() / editor.file)

    dest_path = Path.cwd() / editor.rule_file
    if editor_rule_file.is_dir():
        shutil.copytree(editor_rule_file, dest_path, dirs_exist_ok=True)
    else:
        shutil.copy2(editor_rule_file, dest_path)
