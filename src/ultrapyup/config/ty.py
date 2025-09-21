from pathlib import Path

import toml

from ultrapyup.layout import LayoutDetection
from ultrapyup.utils import ask, log


def _ty_conf_exist() -> bool:
    """Check if Ty configuration already exists in pyproject.toml."""
    pyproject_path = Path.cwd() / "pyproject.toml"
    if not pyproject_path.exists():
        return False

    with open(pyproject_path) as f:
        config = toml.load(f)
        return "tool" in config and "ty" in config["tool"]


def _remove_ty_config_from_pyproject(pyproject_path: Path) -> None:
    """Remove Ty configuration from pyproject.toml."""
    with open(pyproject_path) as f:
        config = toml.load(f)
        if "tool" in config and "ty" in config["tool"]:
            del config["tool"]["ty"]
            # Remove empty tool section if no other tools remain
            if not config["tool"]:
                del config["tool"]

    with open(pyproject_path, "w") as f:
        toml.dump(config, f)


def _create_ty_config(layout: LayoutDetection) -> None:
    """Create Ty configuration in pyproject.toml."""
    pyproject_path = Path.cwd() / "pyproject.toml"

    # Load existing config or create new one
    if pyproject_path.exists():
        with open(pyproject_path) as f:
            config = toml.load(f)
    else:
        config = {}

    # Ensure tool section exists
    if "tool" not in config:
        config["tool"] = {}

    # Add Ty configuration
    config["tool"]["ty"] = {
        "environment": {"root": layout.root_paths},
    }

    with open(pyproject_path, "w") as f:
        toml.dump(config, f)


def ty_config_setup(layout: LayoutDetection) -> None:
    """Set up Ty configuration in pyproject.toml.

    Args:
        layout: Detected project layout information

    This function:
    1. Checks for existing Ty configuration in pyproject.toml
    2. If configuration exists, asks user if they want to overwrite it
    3. Creates or overwrites the Ty configuration based on user choice
    4. Logs the setup process and completion
    """
    ty_conf_exist = _ty_conf_exist()
    if ty_conf_exist:
        overwrite = ask(
            "Ty configuration already exists. Do you want to overwrite it?", choices=["yes", "no"], multiselect=False
        )
        if overwrite != "yes":
            log.info("Keeping existing configuration")
            return None
        _create_ty_config(layout)
        log.info("ty configuration updated in pyproject.toml")
    else:
        _create_ty_config(layout)
        log.title("Ty configuration setup completed")
        log.info("ty configuration added to pyproject.toml")
