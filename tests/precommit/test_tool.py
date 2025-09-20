from pathlib import Path

from ultrapyup.migrate import _migrate_requirements_to_pyproject
from ultrapyup.package_manager.pm import PackageManager
from ultrapyup.precommit.tool import PreCommitTool


class TestPreCommitTool:
    """Tests for PreCommitTool enum class."""

    def test_precommit_tool_enum_values(self) -> None:
        """Test PreCommitTool enum values."""
        assert PreCommitTool.LEFTHOOK.value == "lefthook"
        assert PreCommitTool.PRE_COMMIT.value == "pre-commit"

    def test_precommit_tool_enum_names(self) -> None:
        """Test PreCommitTool enum names."""
        assert PreCommitTool.LEFTHOOK.name == "LEFTHOOK"
        assert PreCommitTool.PRE_COMMIT.name == "PRE_COMMIT"

    def test_precommit_tool_display_name_property(self) -> None:
        """Test display_name property for each precommit tool."""
        assert PreCommitTool.LEFTHOOK.display_name == "Lefthook"
        assert PreCommitTool.PRE_COMMIT.display_name == "Pre-commit"

    def test_precommit_tool_filename_property(self) -> None:
        """Test filename property for each precommit tool."""
        assert PreCommitTool.LEFTHOOK.filename == "lefthook.yaml"
        assert PreCommitTool.PRE_COMMIT.filename == ".pre-commit-config.yaml"

    def test_precommit_tool_install_command_property(self) -> None:
        """Test install_command property for each precommit tool."""
        assert PreCommitTool.LEFTHOOK.install_command == ["lefthook", "install"]
        assert PreCommitTool.PRE_COMMIT.install_command == ["pre-commit", "install"]

    def test_precommit_tool_comparison(self) -> None:
        """Test PreCommitTool comparison with strings."""
        assert PreCommitTool.LEFTHOOK == "lefthook"
        assert PreCommitTool.PRE_COMMIT == "pre-commit"
        assert PreCommitTool.LEFTHOOK != "pre-commit"

    def test_precommit_tool_iteration(self) -> None:
        """Test that we can iterate over all PreCommitTool values."""
        tools = list(PreCommitTool)
        assert len(tools) == 3
        assert PreCommitTool.LEFTHOOK in tools
        assert PreCommitTool.PRE_COMMIT in tools


class TestPreCommitToolSetup:
    """Tests for PreCommitTool setup functionality."""

    def test_setup_lefthook_success(self, python_uv_project: Path) -> None:
        """Test successful setup of Lefthook tool."""
        tool = PreCommitTool.LEFTHOOK
        package_manager = PackageManager.UV
        tool.setup(package_manager)
        target_file = python_uv_project / "lefthook.yaml"
        assert target_file.is_file()

    def test_setup_precommit_success(self, python_uv_project: Path) -> None:
        """Test successful setup of Pre-commit tool."""
        tool = PreCommitTool.PRE_COMMIT
        package_manager = PackageManager.UV
        tool.setup(package_manager)
        target_file = python_uv_project / ".pre-commit-config.yaml"
        assert target_file.is_file()

    def test_setup_overwrites_existing_file(self, python_uv_project: Path) -> None:
        """Test that setup overwrites existing target files."""
        existing_config = python_uv_project / "lefthook.yaml"
        existing_content = "# Existing Lefthook config\nexisting: content"
        existing_config.write_text(existing_content)
        assert existing_config.is_file()

        tool = PreCommitTool.LEFTHOOK
        package_manager = PackageManager.UV
        tool.setup(package_manager)
        assert existing_config.read_text() != existing_content

    def test_setup_with_pip_package_manager(self, python_pip_project: Path) -> None:
        """Test setup with pip package manager."""
        tool = PreCommitTool.PRE_COMMIT
        package_manager = PackageManager.PIP
        _migrate_requirements_to_pyproject(python_pip_project)
        tool.setup(package_manager)
        target_file = python_pip_project / ".pre-commit-config.yaml"
        assert target_file.is_file()

    def test_setup_with_poetry_package_manager(self, python_poetry_project: Path) -> None:
        """Test setup with poetry package manager."""
        tool = PreCommitTool.LEFTHOOK
        package_manager = PackageManager.POETRY
        tool.setup(package_manager)
        target_file = python_poetry_project / "lefthook.yaml"
        assert target_file.is_file()
