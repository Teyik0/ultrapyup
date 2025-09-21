from pathlib import Path

import toml

from ultrapyup.utils import ask, log


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


def _remove_ruff_config_from_pyproject(pyproject_path: Path) -> None:
    with open(pyproject_path) as f:
        config = toml.load(f)
        if "tool" in config and "ruff" in config["tool"]:
            del config["tool"]["ruff"]
            # Remove empty tool section if no other tools remain
            if not config["tool"]:
                del config["tool"]

    with open(pyproject_path, "w") as f:
        toml.dump(config, f)


def _create_ruff_config() -> None:
    """Create ruff.toml and remove any existing Ruff config from pyproject.toml."""
    # Remove existing Ruff config from pyproject.toml if it exists
    pyproject_path = Path.cwd() / "pyproject.toml"
    if pyproject_path.exists():
        _remove_ruff_config_from_pyproject(pyproject_path)

    # Create ruff.toml from template
    current_file = Path(__file__)
    source_dir = current_file.parent.parent / "resources/ruff.toml"
    (Path.cwd() / "ruff.toml").write_text(source_dir.read_text())


def ruff_config_setup() -> None:
    """Set up Ruff configuration by creating a ruff.toml file.

    This function:
    1. Checks for existing Ruff configuration (ruff.toml or pyproject.toml)
    2. If configuration exists, asks user if they want to overwrite it
    3. Creates or overwrites the ruff.toml file based on user choice
    4. Logs the setup process and completion
    """
    ruff_conf_exist = _ruff_conf_exist()
    if ruff_conf_exist:
        overwrite = ask(
            "Ruff configuration already exists. Do you want to overwrite it?", choices=["yes", "no"], multiselect=False
        )
        if overwrite != "yes":
            log.info("keeping existing configuration")
            return None
        _create_ruff_config()
        log.info("ruff configuration updated")
    else:
        _create_ruff_config()
        log.title("Ruff configuration setup completed")
        log.info("ruff.toml created")
