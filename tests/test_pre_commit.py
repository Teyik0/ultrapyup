from unittest.mock import patch

import pytest

from ultrapyup.package_manager import PackageManager
from ultrapyup.pre_commit import PreCommitTool, get_precommit_tool, precommit_setup


class TestGetPrecommitTool:
    """Tests for get_precommit_tool function."""

    def test_select_lefthook(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test selecting Lefthook as pre-commit tool."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = ["Lefthook"]
            result = get_precommit_tool()

            assert result is not None
            assert len(result) == 1
            assert result[0].name == "Lefthook"
            assert result[0].value == "lefthook"
            assert result[0].filename == "lefthook.yaml"

            captured = capsys.readouterr()
            assert "lefthook" in captured.out

    def test_select_precommit(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test selecting Pre-commit as pre-commit tool."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = ["Pre-commit"]
            result = get_precommit_tool()

            assert result is not None
            assert len(result) == 1
            assert result[0].name == "Pre-commit"
            assert result[0].value == "pre-commit"
            assert result[0].filename == ".pre-commit-config.yaml"

            captured = capsys.readouterr()
            assert "pre-commit" in captured.out

    def test_select_multiple_tools(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test selecting multiple pre-commit tools."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = ["Lefthook", "Pre-commit"]
            result = get_precommit_tool()

            assert result is not None
            assert len(result) == 2
            assert result[0].name == "Lefthook"
            assert result[1].name == "Pre-commit"

            captured = capsys.readouterr()
            assert "lefthook" in captured.out
            assert "pre-commit" in captured.out

    def test_skip_selection(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test skipping pre-commit tool selection (Ctrl+C)."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = None
            result = get_precommit_tool()

            assert result is None

            captured = capsys.readouterr()
            assert "none" in captured.out

    def test_empty_selection(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test empty selection (no tools selected)."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = []
            result = get_precommit_tool()

            assert result is None

            captured = capsys.readouterr()
            assert "none" in captured.out

    def test_inquirer_configuration(self) -> None:
        """Test that inquirer is configured correctly."""
        with patch("InquirerPy.inquirer.select") as mock_inquirer:
            mock_inquirer.return_value.execute.return_value = []
            get_precommit_tool()

            # Verify inquirer.select was called with correct parameters
            mock_inquirer.assert_called_once()
            call_args = mock_inquirer.call_args

            assert "Which pre-commit tool would you like to use" in call_args[1]["message"]
            assert call_args[1]["multiselect"] is True
            assert call_args[1]["mandatory"] is False
            assert "skip" in call_args[1]["keybindings"]
            assert call_args[1]["choices"] == ["Lefthook", "Pre-commit"]


class TestPrecommitSetup:
    """Tests for precommit_setup function."""

    def test_precommit_setup_with_poetry_lefthook(self) -> None:
        """Test setting up lefthook with Poetry package manager."""
        with patch("shutil.copy2") as mock_copy:
            with patch("subprocess.run") as mock_run:
                with patch("ultrapyup.pre_commit.PackageManager.add") as mock_add:
                    mock_run.return_value.returncode = 0
                    mock_run.return_value.stderr = ""

                    poetry_manager = PackageManager("poetry", "poetry.lock")
                    lefthook_tool = PreCommitTool("Lefthook", "lefthook", "lefthook.yaml", ["lefthook", "install"])

                    precommit_setup(poetry_manager, lefthook_tool)

                    # Verify file was copied (we don't care about exact paths in this test)
                    mock_copy.assert_called_once()

                    # Verify lefthook package was added
                    mock_add.assert_called_once_with(["lefthook"])

                    # Verify poetry run lefthook install command was executed
                    mock_run.assert_called_once_with(
                        ["poetry", "run", "lefthook", "install"], check=False, capture_output=True, text=True
                    )

    def test_precommit_setup_with_poetry_precommit(self) -> None:
        """Test setting up pre-commit with Poetry package manager."""
        with patch("shutil.copy2") as mock_copy:
            with patch("subprocess.run") as mock_run:
                with patch("ultrapyup.pre_commit.PackageManager.add") as mock_add:
                    mock_run.return_value.returncode = 0
                    mock_run.return_value.stderr = ""

                    poetry_manager = PackageManager("poetry", "poetry.lock")
                    precommit_tool = PreCommitTool(
                        "Pre-commit", "pre-commit", ".pre-commit-config.yaml", ["pre-commit", "install"]
                    )

                    precommit_setup(poetry_manager, precommit_tool)

                    # Verify file was copied (we don't care about exact paths in this test)
                    mock_copy.assert_called_once()

                    # Verify pre-commit package was added
                    mock_add.assert_called_once_with(["pre-commit"])

                    # Verify poetry run pre-commit install command was executed
                    mock_run.assert_called_once_with(
                        ["poetry", "run", "pre-commit", "install"], check=False, capture_output=True, text=True
                    )

    def test_precommit_setup_with_uv(self) -> None:
        """Test setting up lefthook with uv package manager."""
        with patch("shutil.copy2") as mock_copy:
            with patch("subprocess.run") as mock_run:
                with patch("ultrapyup.pre_commit.PackageManager.add") as mock_add:
                    mock_run.return_value.returncode = 0
                    mock_run.return_value.stderr = ""

                    uv_manager = PackageManager("uv", "uv.lock")
                    lefthook_tool = PreCommitTool("Lefthook", "lefthook", "lefthook.yaml", ["lefthook", "install"])

                    precommit_setup(uv_manager, lefthook_tool)

                    # Verify file was copied (we don't care about exact paths in this test)
                    mock_copy.assert_called_once()

                    # Verify lefthook package was added
                    mock_add.assert_called_once_with(["lefthook"])

                    # Verify uv run lefthook install command was executed
                    # Note: shutil.which may return full path, so we check call args more flexibly
                    assert mock_run.call_count == 1
                    call_args = mock_run.call_args[0][0]  # Get the command list
                    assert call_args[1:] == ["run", "lefthook", "install"]  # Skip the uv path
                    assert "uv" in call_args[0]  # Ensure uv is in the command

    def test_precommit_setup_with_unsupported_manager(self) -> None:
        """Test that unsupported package manager raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported package manager: unsupported"):
            unsupported_manager = PackageManager("unsupported", None)
            lefthook_tool = PreCommitTool("Lefthook", "lefthook", "lefthook.yaml", ["lefthook", "install"])

            precommit_setup(unsupported_manager, lefthook_tool)
