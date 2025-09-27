from pathlib import Path

from ultrapyup.editor.rule import EditorRule
from ultrapyup.package_manager import PackageManager


class TestEditorRule:
    """Tests for EditorRule enum class."""

    def test_editor_rule_enum_values(self) -> None:
        """Test EditorRule enum values."""
        assert EditorRule.GITHUB_COPILOT.value == "github-copilot"
        assert EditorRule.CURSOR_AI.value == "cursor-ai"
        assert EditorRule.WINDSURF_AI.value == "windsurf-ai"
        assert EditorRule.CLAUDE_MD.value == "claude-md"
        assert EditorRule.ZED_AI.value == "zed-ai"

    def test_editor_rule_enum_names(self) -> None:
        """Test EditorRule enum names."""
        assert EditorRule.GITHUB_COPILOT.name == "GITHUB_COPILOT"
        assert EditorRule.CURSOR_AI.name == "CURSOR_AI"
        assert EditorRule.WINDSURF_AI.name == "WINDSURF_AI"
        assert EditorRule.CLAUDE_MD.name == "CLAUDE_MD"
        assert EditorRule.ZED_AI.name == "ZED_AI"

    def test_editor_rule_display_name_property(self) -> None:
        """Test display_name property for each editor rule."""
        assert EditorRule.GITHUB_COPILOT.display_name == "GitHub Copilot"
        assert EditorRule.CURSOR_AI.display_name == "Cursor AI"
        assert EditorRule.WINDSURF_AI.display_name == "Windsurf AI"
        assert EditorRule.CLAUDE_MD.display_name == "Claude (CLAUDE.md)"
        assert EditorRule.ZED_AI.display_name == "Zed AI"

    def test_editor_rule_target_file_property(self) -> None:
        """Test target_file property for each editor rule."""
        assert EditorRule.GITHUB_COPILOT.target_file == ".github/copilot-instructions.md"
        assert EditorRule.CURSOR_AI.target_file == ".cursorrules"
        assert EditorRule.WINDSURF_AI.target_file == ".windsurfrules"
        assert EditorRule.CLAUDE_MD.target_file == "CLAUDE.md"
        assert EditorRule.ZED_AI.target_file == ".rules"

    def test_editor_rule_comparison(self) -> None:
        """Test EditorRule comparison with strings."""
        assert EditorRule.GITHUB_COPILOT == "github-copilot"
        assert EditorRule.CURSOR_AI == "cursor-ai"
        assert EditorRule.GITHUB_COPILOT != "cursor-ai"

    def test_editor_rule_iteration(self) -> None:
        """Test that we can iterate over all EditorRule values."""
        rules = list(EditorRule)
        assert len(rules) == 6
        assert EditorRule.GITHUB_COPILOT in rules
        assert EditorRule.CURSOR_AI in rules
        assert EditorRule.WINDSURF_AI in rules
        assert EditorRule.CLAUDE_MD in rules
        assert EditorRule.ZED_AI in rules


class TestEditorRuleSetup:
    """Tests for EditorRule setup functionality."""

    def test_setup_github_copilot_success(self, project_dir: Path) -> None:
        """Test successful setup of GitHub Copilot rule."""
        rule = EditorRule.GITHUB_COPILOT
        rule.setup(PackageManager.UV)
        github_dir = project_dir / ".github"
        target_file = github_dir / "copilot-instructions.md"
        assert github_dir.is_dir()
        assert target_file.is_file()

    def test_setup_cursor_ai_success(self, project_dir: Path) -> None:
        """Test successful setup of Cursor AI rule."""
        rule = EditorRule.CURSOR_AI
        rule.setup(PackageManager.UV)
        target_file = project_dir / ".cursorrules"
        assert target_file.is_file()

    def test_setup_windsurf_ai_success(self, project_dir: Path) -> None:
        """Test successful setup of Windsurf AI rule."""
        rule = EditorRule.WINDSURF_AI
        rule.setup(PackageManager.UV)
        target_file = project_dir / ".windsurfrules"
        assert target_file.is_file()

    def test_setup_claude_md_success(self, project_dir: Path) -> None:
        """Test successful setup of Claude MD rule."""
        rule = EditorRule.CLAUDE_MD
        rule.setup(PackageManager.UV)
        target_file = project_dir / "CLAUDE.md"
        assert target_file.is_file()

    def test_setup_zed_ai_success(self, project_dir: Path) -> None:
        """Test successful setup of Zed AI rule."""
        rule = EditorRule.ZED_AI
        rule.setup(PackageManager.UV)
        target_file = project_dir / ".rules"
        assert target_file.is_file()

    def test_setup_overwrites_existing_file(self, project_dir: Path) -> None:
        """Test that setup overwrites existing target files."""
        existing_rule: Path = project_dir / ".cursorrules"
        existing_rules_content = "# Existing Cursor AI Rules\nUpdated content"
        existing_rule.write_text(existing_rules_content)
        assert existing_rule.is_file()

        rule = EditorRule.CURSOR_AI
        rule.setup(PackageManager.UV)
        # Verify file was overwritten with new content
        assert existing_rule.read_text() != existing_rules_content
