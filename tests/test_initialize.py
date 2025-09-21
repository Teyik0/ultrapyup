from pathlib import Path
from unittest.mock import patch

import pytest
import toml

from ultrapyup.editor import EditorRule, EditorSetting
from ultrapyup.initialize import (
    initialize,
)
from ultrapyup.package_manager import PackageManager
from ultrapyup.precommit import PreCommitTool


class TestInitialize:
    """Tests for the main initialize function."""

    def test_initialize_exits_early_without_project(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test that initialize exits early when no Python project exists."""
        with pytest.raises(RuntimeError, match="Not a Python project"):
            initialize()

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
            assert "ruff, ty" in captured.out  # Dependencies list
            assert "Ruff configuration setup completed" in captured.out  # From ruff_config_setup
            assert "ruff.toml created" in captured.out  # From ruff_config_setup
            assert result is None

            pyproject_path = python_empty_project / "pyproject.toml"
            with open(pyproject_path) as f:
                pyproject_data = toml.load(f)

            dev_deps = pyproject_data.get("dependency-groups", {}).get("dev", [])
            assert any(dep.startswith("ruff>=") for dep in dev_deps)
            assert any(dep.startswith("ty>=") for dep in dev_deps)

    def test_initialize_with_precommit_tool(self, python_uv_project: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Test initialize with pre-commit tools selected."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            # Set up inquirer mock to return choices: no editor rules, no editor settings, lefthook precommit
            mock_inquirer.return_value.execute.side_effect = [[], [], "Lefthook"]

            result = initialize()
            captured = capsys.readouterr()
            assert "uv" in captured.out  # Package manager auto-detected
            assert "Dependencies installed" in captured.out  # From install_dependencies
            assert "lefthook" in captured.out  # Precommit tool in dependencies and logs
            assert "Ruff configuration setup completed" in captured.out  # From ruff_config_setup
            assert "ruff.toml created" in captured.out  # From ruff_config_setup
            assert "Pre-commit setup completed" in captured.out  # From precommit setup
            assert "lefthook.yaml created" in captured.out  # Precommit file created
            assert result is None

            pyproject_path = python_uv_project / "pyproject.toml"
            with open(pyproject_path) as f:
                pyproject_data = toml.load(f)

            dev_deps = pyproject_data.get("dependency-groups", {}).get("dev", [])
            assert any(dep.startswith("ruff>=") for dep in dev_deps)
            assert any(dep.startswith("ty>=") for dep in dev_deps)
            assert any(dep.startswith("lefthook>=") for dep in dev_deps)

            assert (python_uv_project / "lefthook.yaml").exists()
            assert not (python_uv_project / ".pre-commit-config.yaml").exists()
            assert (python_uv_project / "ruff.toml").exists()

    def test_initialize_with_editors(self, python_uv_project: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Test initialize with editors selected."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.side_effect = [["Zed AI"], ["Zed"], []]

            result = initialize()
            captured = capsys.readouterr()
            assert "uv" in captured.out  # Package manager auto-detected
            assert "Dependencies installed" in captured.out  # From install_dependencies
            assert "Ruff configuration setup completed" in captured.out  # From ruff_config_setup
            assert "ruff.toml created" in captured.out  # From ruff_config_setup
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

            assert (python_uv_project / ".rules").exists()
            assert (python_uv_project / ".zed").exists()
            assert not (python_uv_project / ".vscode/settings.json").exists()
            assert (python_uv_project / "ruff.toml").exists()

    def test_initialize_full_flow_with_pip(self, python_pip_project: Path, capsys: pytest.CaptureFixture[str]) -> None:
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
            assert (python_pip_project / "pyproject.toml").exists()

            captured = capsys.readouterr()
            assert "Migrated requirements.txt to pyproject.toml" in captured.out
            assert (
                "Migrated 3 dependencies" in captured.out or "3 dependencies" in captured.out
            )  # From migration (may have ANSI codes)
            assert "pip" in captured.out  # Package manager selection logged
            assert "Dependencies installed" in captured.out  # From install_dependencies
            assert "pre-commit" in captured.out  # Precommit tool in dependencies
            assert "Ruff configuration setup completed" in captured.out  # From ruff_config_setup
            assert "ruff.toml created" in captured.out  # From ruff_config_setup
            assert "Pre-commit setup completed" in captured.out  # From precommit setup
            assert ".pre-commit-config.yaml created" in captured.out  # Precommit file created
            assert "AI rules setup completed" in captured.out  # From editor rule setup
            assert "Editor settings setup completed" in captured.out  # From editor settings setup
            assert ".rules created" in captured.out  # AI rule files created
            assert ".zed created" in captured.out  # Editor settings created
            assert result is None

            pyproject_path = python_pip_project / "pyproject.toml"
            with open(pyproject_path) as f:
                pyproject_data = toml.load(f)

            dev_deps = pyproject_data.get("dependency-groups", {}).get("dev", [])
            assert any(dep.startswith("ruff>=") for dep in dev_deps)
            assert any(dep.startswith("ty>=") for dep in dev_deps)
            assert any(dep.startswith("pre-commit>=") for dep in dev_deps)

            assert (python_pip_project / ".pre-commit-config.yaml").exists()
            assert not (python_pip_project / "lefthook.yaml").exists()
            assert (python_pip_project / ".rules").exists()
            assert (python_pip_project / ".zed").exists()
            assert not (python_pip_project / ".vscode/settings.json").exists()
            assert (python_pip_project / "ruff.toml").exists()

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
            assert "ruff.toml created" in captured.out
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
            assert any(dep.startswith("pre-commit>=") for dep in dev_deps)

            assert (python_uv_project / ".pre-commit-config.yaml").exists()
            assert not (python_uv_project / "lefthook.yaml").exists()
            assert (python_uv_project / ".github/copilot-instructions.md").exists()
            assert not (python_uv_project / ".zed").exists()
            assert (python_uv_project / ".vscode").exists()
            assert (python_uv_project / "ruff.toml").exists()

    def test_initialize_with_cli_parameters(self, python_uv_project: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Test initialize with CLI parameters (non-interactive mode)."""
        result = initialize(
            package_manager=PackageManager.UV,
            editor_rules=[EditorRule.ZED_AI, EditorRule.CURSOR_AI],
            editor_settings=[EditorSetting.VSCODE],
            precommit_tool=PreCommitTool.LEFTHOOK,
        )

        captured = capsys.readouterr()
        assert "uv" in captured.out  # Package manager selection logged
        assert "zed-ai" in captured.out  # Zed AI editor rule logged
        assert "cursor-ai" in captured.out  # Cursor AI editor rule logged
        assert "vscode" in captured.out  # Editor settings selection logged
        assert "lefthook" in captured.out  # Precommit tools selection logged
        assert "Dependencies installed" in captured.out
        assert "ruff, ty, lefthook" in captured.out
        assert "Pre-commit setup completed" in captured.out
        assert "AI rules setup completed" in captured.out
        assert "Editor settings setup completed" in captured.out
        assert result is None

        # Verify files were created
        assert (python_uv_project / "lefthook.yaml").exists()
        assert (python_uv_project / ".cursorrules").exists()
        assert (python_uv_project / ".rules").exists()
        assert (python_uv_project / ".vscode").exists()
        assert (python_uv_project / "ruff.toml").exists()

    def test_initialize_with_empty_cli_parameters(
        self, python_uv_project: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test initialize with empty CLI parameters (skip all optional features)."""
        result = initialize(
            package_manager=PackageManager.SKIP, editor_rules=[], editor_settings=[], precommit_tool=None
        )

        captured = capsys.readouterr()
        assert "uv" in captured.out  # Package manager selection logged
        assert "none" in captured.out  # Should appear 3 times for empty lists
        assert "Dependencies installed" in captured.out
        assert "ruff, ty" in captured.out  # Only core dependencies
        assert "Ruff configuration setup completed" in captured.out
        assert "ruff.toml created" in captured.out
        assert "Pre-commit setup completed" not in captured.out
        assert "AI rules setup completed" not in captured.out
        assert "Editor settings setup completed" not in captured.out
        assert result is None

        # Verify no optional files were created
        assert not (python_uv_project / "lefthook.yaml").exists()
        assert not (python_uv_project / ".cursorrules").exists()
        assert not (python_uv_project / ".vscode").exists()
        # But ruff.toml should always be created
        assert (python_uv_project / "ruff.toml").exists()
