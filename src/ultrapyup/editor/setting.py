import shutil
from enum import Enum
from pathlib import Path


class EditorSetting(str, Enum):
    """Editor settings options with integrated functionality."""

    VSCODE = "vscode"
    CURSOR = "cursor"
    WINDSURF = "windsurf"
    KIRO = "kiro"
    ZED = "zed"
    SKIP = "skip"

    @property
    def display_name(self) -> str:
        """Get the display name for this editor setting."""
        if self == EditorSetting.SKIP:
            raise ValueError("Cannot get display name for SKIP editor setting")
        display_name_map = {
            "vscode": "VSCode",
            "cursor": "Cursor",
            "windsurf": "Windsurf",
            "kiro": "Kiro",
            "zed": "Zed",
        }
        return display_name_map[self.value]

    @property
    def settings_dir(self) -> str:
        """Get the settings directory for this editor."""
        if self == EditorSetting.SKIP:
            raise ValueError("Cannot get settings directory for SKIP editor setting")
        settings_dir_map = {
            "vscode": ".vscode",
            "cursor": ".vscode",
            "windsurf": ".vscode",
            "kiro": ".vscode",
            "zed": ".zed",
        }
        return settings_dir_map[self.value]

    def setup(self) -> None:
        """Set up editor settings by copying configuration directories."""
        current_file = Path(__file__)
        source_dir = current_file.parent.parent / "resources" / self.settings_dir
        target_dir = Path.cwd() / self.settings_dir

        shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
