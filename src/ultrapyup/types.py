from enum import Enum


class EditorRuleType(str, Enum):
    """AI editor rules options."""

    GITHUB_COPILOT = "github-copilot"
    CURSOR_AI = "cursor-ai"
    WINDSURF_AI = "windsurf-ai"
    CLAUDE_MD = "claude-md"
    ZED_AI = "zed-ai"

    @property
    def display_name(self) -> str:
        """Get the display name for this editor rule."""
        display_name_map = {
            "github-copilot": "GitHub Copilot",
            "cursor-ai": "Cursor AI",
            "windsurf-ai": "Windsurf AI",
            "claude-md": "Claude (CLAUDE.md)",
            "zed-ai": "Zed AI",
        }
        return display_name_map[self.value]

    @property
    def target_file(self) -> str:
        """Get the target file for this editor rule."""
        target_file_map = {
            "github-copilot": ".github/copilot-instructions.md",
            "cursor-ai": ".cursorrules",
            "windsurf-ai": ".windsurfrules",
            "claude-md": "CLAUDE.md",
            "zed-ai": ".rules",
        }
        return target_file_map[self.value]

    @property
    def source_file(self) -> str:
        """Get the source file for this editor rule."""
        return ".rules"  # All use the same source file


class EditorSettingType(str, Enum):
    """Editor settings options."""

    VSCODE = "vscode"
    CURSOR = "cursor"
    WINDSURF = "windsurf"
    KIRO = "kiro"
    ZED = "zed"

    @property
    def display_name(self) -> str:
        """Get the display name for this editor setting."""
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
        settings_dir_map = {
            "vscode": ".vscode",
            "cursor": ".vscode",
            "windsurf": ".vscode",
            "kiro": ".vscode",
            "zed": ".zed",
        }
        return settings_dir_map[self.value]


class PreCommitToolType(str, Enum):
    """Pre-commit tools options."""

    LEFTHOOK = "lefthook"
    PRE_COMMIT = "pre-commit"

    @property
    def filename(self) -> str:
        """Get the config filename for this pre-commit tool."""
        filename_map = {
            "lefthook": "lefthook.yaml",
            "pre-commit": ".pre-commit-config.yaml",
        }
        return filename_map[self.value]

    @property
    def install_command(self) -> list[str]:
        """Get the install command for this pre-commit tool."""
        install_command_map = {
            "lefthook": ["lefthook", "install"],
            "pre-commit": ["pre-commit", "install"],
        }
        return install_command_map[self.value]

    @property
    def display_name(self) -> str:
        """Get the display name for this pre-commit tool."""
        display_name_map = {
            "lefthook": "Lefthook",
            "pre-commit": "Pre-commit",
        }
        return display_name_map[self.value]
