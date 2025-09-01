import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from InquirerPy import inquirer

from ultrapyup.utils import log


@dataclass
class PreCommitTool:
    name: str
    value: str
    filename: str


options: list[PreCommitTool] = [
    PreCommitTool("Lefthook", "lefthook", "lefthook.yaml"),
    PreCommitTool("Pre-commit", "pre-commit", ".pre-commit-config.yaml"),
]


def get_precommit_tool() -> list[PreCommitTool] | None:
    values = inquirer.select(
        message="Which pre-commit tool would you like to use ? "
        "(optional - skip with ctrl+c)",
        choices=[pre_commit_tool.name for pre_commit_tool in options],
        multiselect=True,
        qmark="◆ ",
        amark="◇ ",
        pointer="◼ ",
        marker="◻ ",
        marker_pl=" ",
        transformer=lambda result: "",
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


def precommit_setup(add_cmd: str, pre_commit_tool: PreCommitTool):
    current_file = Path(__file__)
    lefthook_source = current_file.parent / "resources" / pre_commit_tool.filename

    shutil.copy2(lefthook_source, Path.cwd() / pre_commit_tool.filename)
    subprocess.run(
        f"{add_cmd} {pre_commit_tool.value} install",
        shell=True,
        capture_output=True,
    )
