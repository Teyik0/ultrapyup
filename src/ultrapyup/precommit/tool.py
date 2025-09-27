import shutil
import subprocess
from enum import Enum
from pathlib import Path

from ultrapyup.package_manager import PackageManager


class PreCommitTool(str, Enum):
    """Pre-commit tools options with integrated functionality."""

    LEFTHOOK = "lefthook"
    PRE_COMMIT = "pre-commit"
    SKIP = "skip"

    @property
    def display_name(self) -> str:
        """Get the display name for this pre-commit tool."""
        if self == PreCommitTool.SKIP:
            raise ValueError("SKIP has no display name")
        display_name_map = {
            "lefthook": "Lefthook",
            "pre-commit": "Pre-commit",
        }
        return display_name_map[self.value]

    @property
    def filename(self) -> str:
        """Get the config filename for this pre-commit tool."""
        if self == PreCommitTool.SKIP:
            raise ValueError("SKIP has no filename")
        filename_map = {
            "lefthook": "lefthook.yaml",
            "pre-commit": ".pre-commit-config.yaml",
        }
        return filename_map[self.value]

    @property
    def install_command(self) -> list[str]:
        """Get the install command for this pre-commit tool."""
        if self == PreCommitTool.SKIP:
            raise ValueError("SKIP has no install command")
        install_command_map = {
            "lefthook": ["lefthook", "install"],
            "pre-commit": ["pre-commit", "install"],
        }
        return install_command_map[self.value]

    def setup(self, package_manager: PackageManager) -> None:
        """Set up pre-commit tool by copying configuration file and installing hooks."""
        current_file = Path(__file__)
        config_source = current_file.parent.parent / "resources" / self.filename
        target_path = Path.cwd() / self.filename

        if config_source.is_file():
            shutil.copy2(config_source, target_path)
        else:
            raise FileNotFoundError(f"Source file {config_source} not found")

        # Install the pre-commit tool as dependency
        package_manager.add([self.value])

        # Install pre-commit hooks
        if package_manager.value == "pip":
            cmd = [shutil.which("python") or "python", "-m", *self.install_command]
        elif package_manager.value == "uv":
            cmd = [shutil.which("uv") or "uv", "run", *self.install_command]
        elif package_manager.value == "poetry":
            cmd = [shutil.which("poetry") or "poetry", "run", *self.install_command]
        else:
            raise ValueError(f"Unsupported package manager for {self.value} install: {package_manager.name}")

        subprocess.run(cmd, check=False, capture_output=True, text=True)
