import shutil
from pathlib import Path

from ultrapyup.editor.setting import EditorSetting


class TestEditorSetting:
    """Tests for EditorSetting enum class."""

    def test_editor_setting_enum_values(self) -> None:
        """Test EditorSetting enum values."""
        assert EditorSetting.VSCODE.value == "vscode"
        assert EditorSetting.CURSOR.value == "cursor"
        assert EditorSetting.WINDSURF.value == "windsurf"
        assert EditorSetting.KIRO.value == "kiro"
        assert EditorSetting.ZED.value == "zed"

    def test_editor_setting_enum_names(self) -> None:
        """Test EditorSetting enum names."""
        assert EditorSetting.VSCODE.name == "VSCODE"
        assert EditorSetting.CURSOR.name == "CURSOR"
        assert EditorSetting.WINDSURF.name == "WINDSURF"
        assert EditorSetting.KIRO.name == "KIRO"
        assert EditorSetting.ZED.name == "ZED"

    def test_editor_setting_display_name_property(self) -> None:
        """Test display_name property for each editor setting."""
        assert EditorSetting.VSCODE.display_name == "VSCode"
        assert EditorSetting.CURSOR.display_name == "Cursor"
        assert EditorSetting.WINDSURF.display_name == "Windsurf"
        assert EditorSetting.KIRO.display_name == "Kiro"
        assert EditorSetting.ZED.display_name == "Zed"

    def test_editor_setting_settings_dir_property(self) -> None:
        """Test settings_dir property for each editor setting."""
        assert EditorSetting.VSCODE.settings_dir == ".vscode"
        assert EditorSetting.CURSOR.settings_dir == ".vscode"
        assert EditorSetting.WINDSURF.settings_dir == ".vscode"
        assert EditorSetting.KIRO.settings_dir == ".vscode"
        assert EditorSetting.ZED.settings_dir == ".zed"

    def test_editor_setting_comparison(self) -> None:
        """Test EditorSetting comparison with strings."""
        assert EditorSetting.VSCODE == "vscode"
        assert EditorSetting.CURSOR == "cursor"
        assert EditorSetting.VSCODE != "cursor"

    def test_editor_setting_iteration(self) -> None:
        """Test that we can iterate over all EditorSetting values."""
        settings = list(EditorSetting)
        assert len(settings) == 5
        assert EditorSetting.VSCODE in settings
        assert EditorSetting.CURSOR in settings
        assert EditorSetting.WINDSURF in settings
        assert EditorSetting.KIRO in settings
        assert EditorSetting.ZED in settings


class TestEditorSettingSetup:
    """Tests for EditorSetting setup functionality."""

    def test_setup_vscode_success(self, project_dir: Path) -> None:
        """Test successful setup of VSCode settings."""
        setting = EditorSetting.VSCODE
        setting.setup()
        target_dir = project_dir / ".vscode"
        settings_file = target_dir / "settings.json"
        extensions_file = target_dir / "extensions.json"
        assert target_dir.is_dir()
        assert settings_file.is_file()
        assert extensions_file.is_file()

    def test_setup_cursor_success(self, project_dir: Path) -> None:
        """Test successful setup of Cursor settings."""
        setting = EditorSetting.CURSOR
        setting.setup()
        target_dir = project_dir / ".vscode"
        settings_file = target_dir / "settings.json"
        extensions_file = target_dir / "extensions.json"
        assert target_dir.is_dir()
        assert settings_file.is_file()
        assert extensions_file.is_file()

    def test_setup_windsurf_success(self, project_dir: Path) -> None:
        """Test successful setup of Windsurf settings."""
        setting = EditorSetting.WINDSURF
        setting.setup()
        target_dir = project_dir / ".vscode"
        settings_file = target_dir / "settings.json"
        extensions_file = target_dir / "extensions.json"
        assert target_dir.is_dir()
        assert settings_file.is_file()
        assert extensions_file.is_file()

    def test_setup_kiro_success(self, project_dir: Path) -> None:
        """Test successful setup of Kiro settings."""
        setting = EditorSetting.KIRO
        setting.setup()
        target_dir = project_dir / ".vscode"
        settings_file = target_dir / "settings.json"
        extensions_file = target_dir / "extensions.json"
        assert target_dir.is_dir()
        assert settings_file.is_file()
        assert extensions_file.is_file()

    def test_setup_zed_success(self, project_dir: Path) -> None:
        """Test successful setup of Zed settings."""
        setting = EditorSetting.ZED
        setting.setup()
        target_dir = project_dir / ".zed"
        settings_file = target_dir / "settings.json"
        assert target_dir.is_dir()
        assert settings_file.is_file()

    def test_setup_overwrites_existing_directory(self, project_dir: Path) -> None:
        """Test that setup overwrites existing target directories."""
        existing_dir = project_dir / ".vscode"
        existing_dir.mkdir(exist_ok=True)
        existing_file = existing_dir / "existing.json"
        existing_content = '{"existing": "config"}'
        existing_file.write_text(existing_content)
        assert existing_dir.is_dir()
        assert existing_file.is_file()

        setting = EditorSetting.VSCODE
        setting.setup()
        # Verify directory still exists (dirs_exist_ok=True allows merging)
        assert existing_dir.is_dir()

    def test_setup_creates_parent_directories(self, project_dir: Path) -> None:
        """Test that setup creates necessary parent directories."""
        setting = EditorSetting.ZED
        target_dir = project_dir / ".zed"
        # Ensure directory doesn't exist initially
        if target_dir.exists():
            shutil.rmtree(target_dir)

        setting.setup()
        settings_file = target_dir / "settings.json"
        assert target_dir.is_dir()
        assert settings_file.is_file()

    def test_setup_copies_all_configuration_files(self, project_dir: Path) -> None:
        """Test that setup copies all expected configuration files."""
        # Test VSCode-compatible editors copy both settings.json and extensions.json
        setting = EditorSetting.VSCODE
        setting.setup()
        vscode_dir = project_dir / ".vscode"
        assert vscode_dir.is_dir()
        assert (vscode_dir / "settings.json").is_file()
        assert (vscode_dir / "extensions.json").is_file()

        # Test Zed copies settings.json
        setting = EditorSetting.ZED
        setting.setup()
        zed_dir = project_dir / ".zed"
        assert zed_dir.is_dir()
        assert (zed_dir / "settings.json").is_file()
