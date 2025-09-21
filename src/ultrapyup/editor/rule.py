from enum import Enum
from pathlib import Path

from ultrapyup.ai_rules import get_rules_file
from ultrapyup.package_manager import PackageManager


class EditorRule(str, Enum):
    """AI editor rules options with integrated functionality."""

    GITHUB_COPILOT = "github-copilot"
    CURSOR_AI = "cursor-ai"
    WINDSURF_AI = "windsurf-ai"
    CLAUDE_MD = "claude-md"
    ZED_AI = "zed-ai"
    SKIP = "skip"

    @property
    def display_name(self) -> str:
        """Get the display name for this editor rule."""
        if self == EditorRule.SKIP:
            raise ValueError("Cannot get display name for SKIP editor rule")
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
        if self == EditorRule.SKIP:
            raise ValueError("Cannot get target file for SKIP editor rule")
        target_file_map = {
            "github-copilot": ".github/copilot-instructions.md",
            "cursor-ai": ".cursorrules",
            "windsurf-ai": ".windsurfrules",
            "claude-md": "CLAUDE.md",
            "zed-ai": ".rules",
        }
        return target_file_map[self.value]

    def setup(self, package_manager: PackageManager) -> None:
        """Set up AI rule files by copying and renaming them."""
        rule_content = get_rules_file(package_manager)
        target_path = Path.cwd() / self.target_file
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(rule_content)
