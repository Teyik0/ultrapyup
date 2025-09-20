from pathlib import Path

import toml

from ultrapyup.utils import log


def _ruff_conf_exist() -> bool:
    """Check if Ruff configuration already exists in pyproject.toml or in ruff.toml."""
    if (Path.cwd() / "ruff.toml").exists():
        return True

    pyproject_path = Path.cwd() / "pyproject.toml"
    if not pyproject_path.exists():
        return False

    with open(pyproject_path) as f:
        config = toml.load(f)
        return "tool" in config and "ruff" in config["tool"]


def _create_ruff_config() -> None:
    current_file = Path(__file__)
    source_dir = current_file.parent.parent / "resources/ruff.toml"
    (Path.cwd() / "ruff.toml").write_text(source_dir.read_text())


def ruff_config_setup() -> None:
    """Set up Ruff configuration by creating a ruff.toml file.

    This function:
    1. Checks for existing Ruff configuration (ruff.toml or pyproject.toml)
    2. If no configuration exists, creates a new ruff.toml file
    3. Logs the setup process and completion
    """
    ruff_conf_exist = _ruff_conf_exist()
    if ruff_conf_exist:
        log.title("Ruff configuration setup skipped")
        log.info("Ruff configuration already exists, skipping")
        return None

    _create_ruff_config()
    log.title("Ruff configuration setup completed")
    log.info("ruff.toml created")
