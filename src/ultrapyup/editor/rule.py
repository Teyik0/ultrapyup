import shutil
from enum import Enum
from pathlib import Path


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
        display_name_map = {
            "github-copilot": "GitHub Copilot",
            "cursor-ai": "Cursor AI",
            "windsurf-ai": "Windsurf AI",
            "claude-md": "Claude (CLAUDE.md)",
            "zed-ai": "Zed AI",
            "skip": "skip",
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

    def setup(self) -> None:
        """Set up AI rule files by copying and renaming them."""
        current_file = Path(__file__)
        source_file = current_file.parent.parent / "resources" / self.source_file
        target_path = Path.cwd() / self.target_file
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if source_file.is_file():
            shutil.copy2(source_file, target_path)
        else:
            raise FileNotFoundError(f"Source file {source_file} not found")
