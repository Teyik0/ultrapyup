from pathlib import Path
from unittest.mock import patch

import pytest
import toml

from ultrapyup.initialize import (
    initialize,
)


class TestInitialize:
    """Tests for the main initialize function."""

    def test_initialize_exits_early_without_project(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test that initialize exits early when no Python project exists."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            # Mock get_package_manager inquire call
            mock_inquirer.return_value.execute.return_value = "uv"
            result = initialize()

            # Should not call inquirer if no project exists
            mock_inquirer.assert_not_called()
            assert result is None

    def test_initialize_with_minimal_project(
        self, python_empty_project: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test initialize with a minimal Python project."""
        # Create pyproject.toml to avoid migration
        (python_empty_project / "pyproject.toml").write_text(
            "[project]\nname = 'test'\nversion = '0.1.0'\nrequires-python = '>=3.10'"
        )

        # Only mock inquirer to control user choices
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            # Set up inquirer mock to return choices for package manager, editor rules, editor settings, and precommit
            mock_inquirer.return_value.execute.side_effect = ["uv", [], [], []]

            result = initialize()
            captured = capsys.readouterr()
            assert "uv" in captured.out  # Package manager selection logged
            assert "Dependencies installed" in captured.out  # From install_dependencies
            assert "ruff, ty, ultrapyup" in captured.out  # Dependencies list
            assert "Ruff configuration setup completed" in captured.out  # From ruff_config_setup
            assert result is None

            pyproject_path = python_empty_project / "pyproject.toml"
            with open(pyproject_path) as f:
                pyproject_data = toml.load(f)

            dev_deps = pyproject_data.get("dependency-groups", {}).get("dev", [])
            assert any(dep.startswith("ruff>=") for dep in dev_deps)
            assert any(dep.startswith("ty>=") for dep in dev_deps)
            assert any(dep.startswith("ultrapyup>=") for dep in dev_deps)

    def test_initialize_with_precommit_tools(self, python_uv_project: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Test initialize with pre-commit tools selected."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            # Set up inquirer mock to return choices: no editor rules, no editor settings, lefthook precommit
            mock_inquirer.return_value.execute.side_effect = [[], [], ["Lefthook"]]

            result = initialize()
            captured = capsys.readouterr()
            assert "uv" in captured.out  # Package manager auto-detected
            assert "Dependencies installed" in captured.out  # From install_dependencies
            assert "lefthook" in captured.out  # Precommit tool in dependencies and logs
            assert "Ruff configuration setup completed" in captured.out  # From ruff_config_setup
            assert "Pre-commit setup completed" in captured.out  # From precommit setup
            assert "lefthook.yaml created" in captured.out  # Precommit file created
            assert result is None

            pyproject_path = python_uv_project / "pyproject.toml"
            with open(pyproject_path) as f:
                pyproject_data = toml.load(f)

            dev_deps = pyproject_data.get("dependency-groups", {}).get("dev", [])
            assert any(dep.startswith("ruff>=") for dep in dev_deps)
            assert any(dep.startswith("ty>=") for dep in dev_deps)
            assert any(dep.startswith("ultrapyup>=") for dep in dev_deps)
            assert any(dep.startswith("lefthook>=") for dep in dev_deps)

            assert (python_uv_project / "lefthook.yaml").exists()
            assert not (python_uv_project / ".pre-commit-config.yaml").exists()

    def test_initialize_with_editors(self, python_uv_project: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Test initialize with editors selected."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.side_effect = [["Zed AI"], ["Zed"], []]

            result = initialize()
            captured = capsys.readouterr()
            assert "uv" in captured.out  # Package manager auto-detected
            assert "Dependencies installed" in captured.out  # From install_dependencies
            assert "Ruff configuration setup completed" in captured.out  # From ruff_config_setup
            assert "AI rules setup completed" in captured.out  # From editor rule setup
            assert "Editor settings setup completed" in captured.out  # From editor settings setup
            assert ".rules created" in captured.out  # AI rule files created
            assert ".zed created" in captured.out  # Editor settings created
            assert result is None

            pyproject_path = python_uv_project / "pyproject.toml"
            with open(pyproject_path) as f:
                pyproject_data = toml.load(f)

            dev_deps = pyproject_data.get("dependency-groups", {}).get("dev", [])
            assert any(dep.startswith("ruff>=") for dep in dev_deps)
            assert any(dep.startswith("ty>=") for dep in dev_deps)
            assert any(dep.startswith("ultrapyup>=") for dep in dev_deps)

            assert (python_uv_project / ".rules").exists()
            assert (python_uv_project / ".zed").exists()
            assert not (python_uv_project / ".vscode/settings.json").exists()

    def test_initialize_full_flow_with_pip(
        self, project_with_requirements: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test complete initialization flow with all options."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            # Set up inquirer mock to return choices: pip package manager, Zed AI rules, Zed settings, Pre-commit
            mock_inquirer.return_value.execute.side_effect = [
                "pip",
                ["Zed AI"],
                ["Zed"],
                ["Pre-commit"],
            ]

            result = initialize()
            assert (project_with_requirements / "pyproject.toml").exists()

            captured = capsys.readouterr()
            assert "Migrated requirements.txt to pyproject.toml" in captured.out
            assert (
                "Found 4 dependencies" in captured.out or "4 dependencies" in captured.out
            )  # From migration (may have ANSI codes)
            assert "pip" in captured.out  # Package manager selection logged
            assert "Dependencies installed" in captured.out  # From install_dependencies
            assert "pre-commit" in captured.out  # Precommit tool in dependencies
            assert "Ruff configuration setup completed" in captured.out  # From ruff_config_setup
            assert "Pre-commit setup completed" in captured.out  # From precommit setup
            assert ".pre-commit-config.yaml created" in captured.out  # Precommit file created
            assert "AI rules setup completed" in captured.out  # From editor rule setup
            assert "Editor settings setup completed" in captured.out  # From editor settings setup
            assert ".rules created" in captured.out  # AI rule files created
            assert ".zed created" in captured.out  # Editor settings created
            assert result is None

            pyproject_path = project_with_requirements / "pyproject.toml"
            with open(pyproject_path) as f:
                pyproject_data = toml.load(f)

            dev_deps = pyproject_data.get("dependency-groups", {}).get("dev", [])
            assert any(dep.startswith("ruff>=") for dep in dev_deps)
            assert any(dep.startswith("ty>=") for dep in dev_deps)
            assert any(dep.startswith("ultrapyup>=") for dep in dev_deps)
            assert any(dep.startswith("pre-commit>=") for dep in dev_deps)

            assert (project_with_requirements / ".pre-commit-config.yaml").exists()
            assert not (project_with_requirements / "lefthook.yaml").exists()
            assert (project_with_requirements / ".rules").exists()
            assert (project_with_requirements / ".zed").exists()
            assert not (project_with_requirements / ".vscode/settings.json").exists()

    def test_initialize_full_flow_with_uv(self, python_uv_project: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Test complete initialization flow with all options."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.side_effect = [
                ["GitHub Copilot"],
                ["VSCode"],
                ["Pre-commit"],
            ]

            result = initialize()

            captured = capsys.readouterr()
            assert "Package manager auto detected" in captured.out
            assert "uv" in captured.out
            assert "Dependencies installed" in captured.out
            assert "pre-commit" in captured.out
            assert "Ruff configuration setup completed" in captured.out
            assert "Pre-commit setup completed" in captured.out
            assert ".pre-commit-config.yaml created" in captured.out
            assert "AI rules setup completed" in captured.out
            assert "Editor settings setup completed" in captured.out
            assert ".github/copilot-instructions.md created" in captured.out
            assert ".vscode created" in captured.out
            assert result is None

            pyproject_path = python_uv_project / "pyproject.toml"
            with open(pyproject_path) as f:
                pyproject_data = toml.load(f)

            dev_deps = pyproject_data.get("dependency-groups", {}).get("dev", [])
            assert any(dep.startswith("ruff>=") for dep in dev_deps)
            assert any(dep.startswith("ty>=") for dep in dev_deps)
            assert any(dep.startswith("ultrapyup>=") for dep in dev_deps)
            assert any(dep.startswith("pre-commit>=") for dep in dev_deps)

            assert (python_uv_project / ".pre-commit-config.yaml").exists()
            assert not (python_uv_project / "lefthook.yaml").exists()
            assert (python_uv_project / ".github/copilot-instructions.md").exists()
            assert not (python_uv_project / ".zed").exists()
            assert (python_uv_project / ".vscode").exists()
