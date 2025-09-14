from pathlib import Path
from unittest.mock import patch

import pytest

from ultrapyup.editor.rule import EditorRule


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

    def test_editor_rule_source_file_property(self) -> None:
        """Test source_file property for each editor rule."""
        # All rules use the same source file
        for rule in EditorRule:
            assert rule.source_file == ".rules"

    def test_editor_rule_comparison(self) -> None:
        """Test EditorRule comparison with strings."""
        assert EditorRule.GITHUB_COPILOT == "github-copilot"
        assert EditorRule.CURSOR_AI == "cursor-ai"
        assert EditorRule.GITHUB_COPILOT != "cursor-ai"

    def test_editor_rule_iteration(self) -> None:
        """Test that we can iterate over all EditorRule values."""
        rules = list(EditorRule)
        assert len(rules) == 5
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
        rule.setup()

        github_dir = project_dir / ".github"
        target_file = github_dir / "copilot-instructions.md"
        assert github_dir.exists()
        assert github_dir.is_dir()
        assert target_file.exists()

    def test_setup_cursor_ai_success(self, temp_dir: Path) -> None:
        """Test successful setup of Cursor AI rule."""
        # Create resources directory structure
        src_dir = temp_dir / "src" / "ultrapyup"
        resources_dir = src_dir / "resources"
        resources_dir.mkdir(parents=True)

        # Create source .rules file
        rules_content = "# Cursor AI Rules\nTest content for Cursor AI"
        (resources_dir / ".rules").write_text(rules_content)

        rule = EditorRule.CURSOR_AI

        with patch("ultrapyup.editor.rule.Path") as mock_path_class:
            mock_file_path = src_dir / "editor" / "rule.py"
            mock_path_class.return_value = mock_file_path
            mock_path_class.cwd.return_value = temp_dir

            rule.setup()

        # Verify .cursorrules file was created at root
        target_file = temp_dir / ".cursorrules"
        assert target_file.exists()
        assert target_file.read_text() == rules_content

    def test_setup_windsurf_ai_success(self, temp_dir: Path) -> None:
        """Test successful setup of Windsurf AI rule."""
        src_dir = temp_dir / "src" / "ultrapyup"
        resources_dir = src_dir / "resources"
        resources_dir.mkdir(parents=True)

        rules_content = "# Windsurf AI Rules\nTest content for Windsurf AI"
        (resources_dir / ".rules").write_text(rules_content)

        rule = EditorRule.WINDSURF_AI

        with patch("ultrapyup.editor.rule.Path") as mock_path_class:
            mock_file_path = src_dir / "editor" / "rule.py"
            mock_path_class.return_value = mock_file_path
            mock_path_class.cwd.return_value = temp_dir

            rule.setup()

        target_file = temp_dir / ".windsurfrules"
        assert target_file.exists()
        assert target_file.read_text() == rules_content

    def test_setup_claude_md_success(self, temp_dir: Path) -> None:
        """Test successful setup of Claude MD rule."""
        src_dir = temp_dir / "src" / "ultrapyup"
        resources_dir = src_dir / "resources"
        resources_dir.mkdir(parents=True)

        rules_content = "# Claude AI Rules\nTest content for Claude"
        (resources_dir / ".rules").write_text(rules_content)

        rule = EditorRule.CLAUDE_MD

        with patch("ultrapyup.editor.rule.Path") as mock_path_class:
            mock_file_path = src_dir / "editor" / "rule.py"
            mock_path_class.return_value = mock_file_path
            mock_path_class.cwd.return_value = temp_dir

            rule.setup()

        target_file = temp_dir / "CLAUDE.md"
        assert target_file.exists()
        assert target_file.read_text() == rules_content

    def test_setup_zed_ai_success(self, temp_dir: Path) -> None:
        """Test successful setup of Zed AI rule."""
        src_dir = temp_dir / "src" / "ultrapyup"
        resources_dir = src_dir / "resources"
        resources_dir.mkdir(parents=True)

        rules_content = "# Zed AI Rules\nTest content for Zed"
        (resources_dir / ".rules").write_text(rules_content)

        rule = EditorRule.ZED_AI

        with patch("ultrapyup.editor.rule.Path") as mock_path_class:
            mock_file_path = src_dir / "editor" / "rule.py"
            mock_path_class.return_value = mock_file_path
            mock_path_class.cwd.return_value = temp_dir

            rule.setup()

        target_file = temp_dir / ".rules"
        assert target_file.exists()
        assert target_file.read_text() == rules_content

    def test_setup_creates_parent_directories(self, temp_dir: Path) -> None:
        """Test that setup creates parent directories when needed."""
        src_dir = temp_dir / "src" / "ultrapyup"
        resources_dir = src_dir / "resources"
        resources_dir.mkdir(parents=True)

        rules_content = "# GitHub Copilot Rules"
        (resources_dir / ".rules").write_text(rules_content)

        rule = EditorRule.GITHUB_COPILOT

        with patch("ultrapyup.editor.rule.Path") as mock_path_class:
            mock_file_path = src_dir / "editor" / "rule.py"
            mock_path_class.return_value = mock_file_path
            mock_path_class.cwd.return_value = temp_dir

            rule.setup()

        # Verify that .github directory was created
        github_dir = temp_dir / ".github"
        assert github_dir.exists()
        assert github_dir.is_dir()

        target_file = github_dir / "copilot-instructions.md"
        assert target_file.exists()

    def test_setup_overwrites_existing_file(self, temp_dir: Path) -> None:
        """Test that setup overwrites existing target files."""
        src_dir = temp_dir / "src" / "ultrapyup"
        resources_dir = src_dir / "resources"
        resources_dir.mkdir(parents=True)

        # Create new rules content
        new_rules_content = "# New Cursor AI Rules\nUpdated content"
        (resources_dir / ".rules").write_text(new_rules_content)

        # Create existing .cursorrules file with old content
        existing_file = temp_dir / ".cursorrules"
        existing_file.write_text("# Old rules\nOld content")

        rule = EditorRule.CURSOR_AI

        with patch("ultrapyup.editor.rule.Path") as mock_path_class:
            mock_file_path = src_dir / "editor" / "rule.py"
            mock_path_class.return_value = mock_file_path
            mock_path_class.cwd.return_value = temp_dir

            rule.setup()

        # Verify file was overwritten with new content
        assert existing_file.read_text() == new_rules_content

    def test_setup_missing_source_file(self, temp_dir: Path) -> None:
        """Test that setup raises FileNotFoundError when source file is missing."""
        src_dir = temp_dir / "src" / "ultrapyup"
        resources_dir = src_dir / "resources"
        resources_dir.mkdir(parents=True)
        # Don't create the .rules file

        rule = EditorRule.GITHUB_COPILOT

        with patch("ultrapyup.editor.rule.Path") as mock_path_class:
            mock_file_path = src_dir / "editor" / "rule.py"
            mock_path_class.return_value = mock_file_path
            mock_path_class.cwd.return_value = temp_dir

            with pytest.raises(FileNotFoundError, match="Source file .* not found"):
                rule.setup()

    def test_setup_preserves_file_metadata(self, temp_dir: Path) -> None:
        """Test that setup preserves file metadata using shutil.copy2."""
        src_dir = temp_dir / "src" / "ultrapyup"
        resources_dir = src_dir / "resources"
        resources_dir.mkdir(parents=True)

        rules_content = "# Test Rules"
        source_file = resources_dir / ".rules"
        source_file.write_text(rules_content)

        # Set specific permissions on source file
        source_file.chmod(0o644)

        rule = EditorRule.CURSOR_AI

        with patch("ultrapyup.editor.rule.Path") as mock_path_class:
            mock_file_path = src_dir / "editor" / "rule.py"
            mock_path_class.return_value = mock_file_path
            mock_path_class.cwd.return_value = temp_dir

            # Mock shutil.copy2 to verify it's called
            with patch("ultrapyup.editor.rule.shutil.copy2") as mock_copy2:
                rule.setup()
                mock_copy2.assert_called_once()
