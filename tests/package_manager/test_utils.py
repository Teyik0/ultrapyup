from pathlib import Path
from unittest.mock import patch

import pytest

from ultrapyup.package_manager.utils import _package_manager_ask, _package_manager_auto_detect


class TestPackageManagerAsk:
    """Tests for _package_manager_ask function."""

    def test_package_manager_ask_success_uv(self) -> None:
        """Test user prompt for package manager selection."""
        with patch("ultrapyup.package_manager.utils.ask") as mock_inquirer:
            mock_inquirer.return_value = "uv"
            result = _package_manager_ask()

            assert result.value == "uv"
            assert result.lockfile == "uv.lock"

    def test_package_manager_ask_success_poetry(self) -> None:
        """Test user prompt for package manager selection."""
        with patch("ultrapyup.package_manager.utils.ask") as mock_inquirer:
            mock_inquirer.return_value = "poetry"
            result = _package_manager_ask()

            assert result.value == "poetry"
            assert result.lockfile == "poetry.lock"

    def test_package_manager_ask_success_pip(self) -> None:
        """Test user prompt for package manager selection."""
        with patch("ultrapyup.package_manager.utils.ask") as mock_inquirer:
            mock_inquirer.return_value = "pip"
            result = _package_manager_ask()

            assert result.value == "pip"
            assert result.lockfile is None

    def test_package_manager_failure(self) -> None:
        """Test user prompt for package manager selection."""
        with patch("ultrapyup.package_manager.utils.ask") as mock_inquirer:
            mock_inquirer.return_value = "pm"
            with pytest.raises(ValueError, match="Unknown package manager: pm"):
                _package_manager_ask()


class TestPackageManagerAutoDetect:
    """Tests for _package_manager_auto_detect function."""

    def test_package_manager_success_auto_detect_uv(self, python_uv_project: Path) -> None:  # noqa: ARG002
        """Test auto-detection of package manager based on lockfiles."""
        result = _package_manager_auto_detect()
        assert result is not None
        assert result.value == "uv"
        assert result.lockfile == "uv.lock"

    def test_package_manager_success_auto_detect_poetry(self, python_poetry_project: Path) -> None:  # noqa: ARG002
        """Test auto-detection of package manager based on lockfiles."""
        result = _package_manager_auto_detect()
        assert result is not None
        assert result.value == "poetry"
        assert result.lockfile == "poetry.lock"

    def test_package_manager_detect_none_on_pip_project(self, python_pip_project: Path) -> None:  # noqa: ARG002
        """Test auto-detection of package manager when no lockfiles are present."""
        result = _package_manager_auto_detect()
        assert result is None

    def test_package_manager_detect_none_on_empty_project(self, python_empty_project: Path) -> None:  # noqa: ARG002
        """Test auto-detection of package manager when no lockfiles are present."""
        result = _package_manager_auto_detect()
        assert result is None
