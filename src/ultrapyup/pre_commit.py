import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from InquirerPy import inquirer

from ultrapyup.package_manager import PackageManager
from ultrapyup.utils import log


@dataclass
class PreCommitTool:
    """Represents a pre-commit tool configuration."""

    name: str
    value: str
    filename: str


options: list[PreCommitTool] = [
    PreCommitTool("Lefthook", "lefthook", "lefthook.yaml"),
    PreCommitTool("Pre-commit", "pre-commit", ".pre-commit-config.yaml"),
]


def get_precommit_tool() -> list[PreCommitTool] | None:
    """Get the selected pre-commit tools from user input."""
    values = inquirer.select(
        message="Which pre-commit tool would you like to use ? (optional - skip with ctrl+c)",
        choices=[pre_commit_tool.name for pre_commit_tool in options],
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

    pre_commit_tools: list[PreCommitTool] = [pc for pc in options if pc.name in values]

    log.info(", ".join(pre_commit_tool.value for pre_commit_tool in pre_commit_tools))
    return pre_commit_tools


def precommit_setup(package_manager: PackageManager, pre_commit_tool: PreCommitTool) -> None:
    """Set up pre-commit tool by copying configuration file and installing hooks."""
    current_file = Path(__file__)
    lefthook_source = current_file.parent / "resources" / pre_commit_tool.filename

    shutil.copy2(lefthook_source, Path.cwd() / pre_commit_tool.filename)

    # Install the pre-commit tool if it's not already installed
    package_manager.add([pre_commit_tool.value])

    # Install hooks for tools like lefthook
    if pre_commit_tool.value == "lefthook":
        if package_manager.name == "pip":
            subprocess.run(
                [shutil.which("python") or "python", "-m", "lefthook", "install"],
                check=False,
                capture_output=True,
            )
        elif package_manager.name == "uv":
            subprocess.run(
                [shutil.which("uv") or "uv", "run", "lefthook", "install"],
                check=False,
                capture_output=True,
            )
        else:
            raise ValueError(f"Unsupported package manager for lefthook install: {package_manager.name}")
