from pathlib import Path

import pytest
import toml

from ultrapyup.layout import (
    LayoutDetection,
    ProjectLayout,
    apply_ty_config,
    detect_project_layout,
    generate_ty_config,
    get_layout_info,
)


class TestProjectLayoutDetection:
    """Test suite for project layout detection functionality."""

    def test_detect_src_layout(self, project_dir: Path) -> None:
        """Test detection of src/ layout with package structure."""
        # Arrange
        src_dir = project_dir / "src"
        src_dir.mkdir()
        package_dir = src_dir / "mypackage"
        package_dir.mkdir()
        (package_dir / "__init__.py").touch()
        (project_dir / "pyproject.toml").touch()

        # Act
        layout = detect_project_layout()

        # Assert
        assert layout.layout == ProjectLayout.SRC_LAYOUT
        assert layout.root_paths == ["./src"]
        assert layout.package_name == "mypackage"

    def test_detect_flat_layout(self, project_dir: Path) -> None:
        """Test detection of flat layout with Python files in root."""
        # Arrange
        (project_dir / "main.py").touch()
        (project_dir / "utils.py").touch()
        (project_dir / "pyproject.toml").touch()

        # Act
        layout = detect_project_layout()

        # Assert
        assert layout.layout == ProjectLayout.FLAT_LAYOUT
        assert layout.root_paths == ["./"]
        assert layout.package_name is None

    def test_detect_package_layout(self, project_dir: Path) -> None:
        """Test detection of package layout with pyproject.toml configuration."""
        pyproject_content = """
[project]
name = "my-awesome-package"
version = "0.1.0"
"""
        (project_dir / "pyproject.toml").write_text(pyproject_content)

        package_dir = project_dir / "my_awesome_package"
        package_dir.mkdir()
        (package_dir / "__init__.py").touch()
        (package_dir / "main.py").touch()

        # Act
        layout = detect_project_layout()

        # Assert
        assert layout.layout == ProjectLayout.PACKAGE_LAYOUT
        assert layout.root_paths == ["./"]
        assert layout.package_name == "my_awesome_package"

    def test_detect_app_layout(self, project_dir: Path) -> None:
        """Test detection of app/ layout structure."""
        # Arrange
        app_dir = project_dir / "app"
        app_dir.mkdir()
        (app_dir / "main.py").touch()
        (app_dir / "models.py").touch()
        (project_dir / "pyproject.toml").touch()

        # Act
        layout = detect_project_layout()

        # Assert
        assert layout.layout == ProjectLayout.APP_LAYOUT
        assert layout.root_paths == ["./app"]
        assert layout.package_name == "app"

    def test_detect_unknown_layout(self, project_dir: Path) -> None:
        """Test fallback to unknown layout when no patterns match."""
        # Arrange - create minimal structure that doesn't match known patterns
        (project_dir / "README.md").touch()

        # Act
        layout = detect_project_layout()

        # Assert
        assert layout.layout == ProjectLayout.UNKNOWN
        assert layout.root_paths == ["./"]
        assert layout.package_name is None

    def test_layout_priority_src_over_package(self, project_dir: Path) -> None:
        """Test that src/ layout takes priority over package layout."""
        pyproject_content = """
[project]
name = "testpackage"
version = "0.1.0"
"""
        (project_dir / "pyproject.toml").write_text(pyproject_content)

        # Create both src/ and package/ structures
        src_dir = project_dir / "src"
        src_dir.mkdir()
        (src_dir / "testpackage").mkdir()
        (src_dir / "testpackage" / "__init__.py").touch()

        package_dir = project_dir / "testpackage"
        package_dir.mkdir()
        (package_dir / "__init__.py").touch()

        # Act
        layout = detect_project_layout()

        # Assert - src/ layout should take priority
        assert layout.layout == ProjectLayout.SRC_LAYOUT
        assert layout.root_paths == ["./src"]

    def test_complex_src_layout_multiple_packages(self, project_dir: Path) -> None:
        """Test src layout detection with multiple packages."""
        # Arrange
        src_dir = project_dir / "src"
        src_dir.mkdir()

        # Create multiple packages
        for package_name in ["package1", "package2"]:
            package_dir = src_dir / package_name
            package_dir.mkdir()
            (package_dir / "__init__.py").touch()

        (project_dir / "pyproject.toml").touch()

        # Act
        layout = detect_project_layout()

        # Assert
        assert layout.layout == ProjectLayout.SRC_LAYOUT
        assert layout.root_paths == ["./src"]
        # Should pick one of the packages found
        assert layout.package_name in ["package1", "package2"]

    def test_empty_src_directory(self, project_dir: Path) -> None:
        """Test src directory detection with no packages."""
        # Arrange
        src_dir = project_dir / "src"
        src_dir.mkdir()
        (project_dir / "pyproject.toml").touch()

        # Act
        layout = detect_project_layout()

        # Assert
        assert layout.layout == ProjectLayout.SRC_LAYOUT
        assert layout.root_paths == ["./src"]
        assert layout.package_name is None


class TestTyConfigGeneration:
    """Test suite for Ty configuration generation."""

    def test_generate_ty_config_src_layout(self) -> None:
        """Test Ty config generation for src layout."""
        # Arrange
        layout = LayoutDetection(layout=ProjectLayout.SRC_LAYOUT, root_paths=["./src"], package_name="mypackage")

        # Act
        config = generate_ty_config(layout)

        # Assert
        assert config["tool"]["ty"]["environment"]["root"] == ["./src"]
        assert "src" in config["tool"]["ty"]["src"]["include"]
        assert "tests" in config["tool"]["ty"]["src"]["include"]
        assert "**/__pycache__" in config["tool"]["ty"]["src"]["exclude"]
        assert config["tool"]["ty"]["rules"]["division-by-zero"] == "error"

    def test_generate_ty_config_app_layout(self) -> None:
        """Test Ty config generation for app layout."""
        # Arrange
        layout = LayoutDetection(layout=ProjectLayout.APP_LAYOUT, root_paths=["./app"], package_name="app")

        # Act
        config = generate_ty_config(layout)

        # Assert
        assert config["tool"]["ty"]["environment"]["root"] == ["./app"]
        assert "app" in config["tool"]["ty"]["src"]["include"]
        assert "tests" in config["tool"]["ty"]["src"]["include"]

    def test_generate_ty_config_package_layout(self) -> None:
        """Test Ty config generation for package layout."""
        # Arrange
        layout = LayoutDetection(layout=ProjectLayout.PACKAGE_LAYOUT, root_paths=["./"], package_name="mypackage")

        # Act
        config = generate_ty_config(layout)

        # Assert
        assert config["tool"]["ty"]["environment"]["root"] == ["./"]
        assert "mypackage" in config["tool"]["ty"]["src"]["include"]
        assert "mypackage/**/generated/**" in config["tool"]["ty"]["src"]["exclude"]

    def test_generate_ty_config_flat_layout(self) -> None:
        """Test Ty config generation for flat layout."""
        # Arrange
        layout = LayoutDetection(layout=ProjectLayout.FLAT_LAYOUT, root_paths=["./"], package_name=None)

        # Act
        config = generate_ty_config(layout)

        # Assert
        assert config["tool"]["ty"]["environment"]["root"] == ["./"]
        # No specific includes for flat layout
        assert "include" not in config["tool"]["ty"]["src"]


class TestTyConfigApplication:
    """Test suite for applying Ty configuration to pyproject.toml."""

    def test_apply_ty_config_success(self, project_dir: Path) -> None:
        """Test successful application of Ty config to pyproject.toml."""
        # Arrange
        pyproject_content = """
[project]
name = "test-project"
version = "0.1.0"

[build-system]
requires = ["setuptools"]
"""
        (project_dir / "pyproject.toml").write_text(pyproject_content)

        layout = LayoutDetection(layout=ProjectLayout.SRC_LAYOUT, root_paths=["./src"], package_name="test_project")

        # Act
        apply_ty_config(layout)

        # Assert
        with open(project_dir / "pyproject.toml") as f:
            config = toml.load(f)

        assert "tool" in config
        assert "ty" in config["tool"]
        assert config["tool"]["ty"]["environment"]["root"] == ["./src"]
        assert "rules" in config["tool"]["ty"]

    def test_apply_ty_config_missing_file(self, project_dir: Path) -> None:  # noqa: ARG002
        """Test error handling when pyproject.toml doesn't exist."""
        # Arrange
        layout = LayoutDetection(layout=ProjectLayout.SRC_LAYOUT, root_paths=["./src"], package_name="test")

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            apply_ty_config(layout)


class TestLayoutInfo:
    """Test suite for layout information formatting."""

    def test_get_layout_info_with_package(self) -> None:
        """Test layout information formatting with package name."""
        # Arrange
        layout = LayoutDetection(
            layout=ProjectLayout.SRC_LAYOUT, root_paths=["./src", "./lib"], package_name="mypackage"
        )

        # Act
        info = get_layout_info(layout)

        # Assert
        assert "Source layout (src/ directory)" in info
        assert "Root paths: ./src, ./lib" in info
        assert "Main package: mypackage" in info

    def test_get_layout_info_without_package(self) -> None:
        """Test layout information formatting without package name."""
        # Arrange
        layout = LayoutDetection(layout=ProjectLayout.FLAT_LAYOUT, root_paths=["./"], package_name=None)

        # Act
        info = get_layout_info(layout)

        # Assert
        assert "Flat layout (files in project root)" in info
        assert "Root paths: ./" in info
        assert "Main package:" not in info

    @pytest.mark.parametrize(
        ("layout_type", "expected_description"),
        [
            (ProjectLayout.SRC_LAYOUT, "Source layout (src/ directory)"),
            (ProjectLayout.FLAT_LAYOUT, "Flat layout (files in project root)"),
            (ProjectLayout.PACKAGE_LAYOUT, "Package layout (package_name/package_name structure)"),
            (ProjectLayout.APP_LAYOUT, "Application layout (app/ directory)"),
            (ProjectLayout.UNKNOWN, "Unknown layout"),
        ],
    )
    def test_layout_descriptions(self, layout_type: ProjectLayout, expected_description: str) -> None:
        """Test layout description strings for all layout types."""
        # Arrange
        layout = LayoutDetection(layout=layout_type, root_paths=["./"], package_name=None)

        # Act
        info = get_layout_info(layout)

        # Assert
        assert expected_description in info


class TestEdgeCases:
    """Test suite for edge cases and error paths."""

    def test_get_project_name_invalid_toml(self, project_dir: Path) -> None:
        """Test _get_project_name with invalid TOML content."""
        # Arrange - create invalid TOML
        (project_dir / "pyproject.toml").write_text("invalid toml content [[[")

        # Act
        layout = detect_project_layout()

        # Assert - should fallback to unknown layout
        assert layout.layout == ProjectLayout.UNKNOWN

    def test_get_project_name_no_project_section(self, project_dir: Path) -> None:
        """Test _get_project_name with TOML missing project section."""
        # Arrange
        pyproject_content = """
[build-system]
requires = ["setuptools"]
"""
        (project_dir / "pyproject.toml").write_text(pyproject_content)

        # Act
        layout = detect_project_layout()

        # Assert - should fallback to unknown layout
        assert layout.layout == ProjectLayout.UNKNOWN

    def test_detect_src_layout_no_packages(self, project_dir: Path) -> None:
        """Test src layout detection when src exists but has no Python packages."""
        # Arrange
        src_dir = project_dir / "src"
        src_dir.mkdir()
        # Create files but no packages (no __init__.py)
        (src_dir / "random_file.txt").touch()
        (project_dir / "pyproject.toml").touch()

        # Act
        layout = detect_project_layout()

        # Assert
        assert layout.layout == ProjectLayout.SRC_LAYOUT
        assert layout.package_name is None

    def test_detect_package_layout_no_python_files(self, project_dir: Path) -> None:
        """Test package layout when package dir exists but has no Python files."""
        # Arrange
        pyproject_content = """
[project]
name = "test-package"
version = "0.1.0"
"""
        (project_dir / "pyproject.toml").write_text(pyproject_content)

        package_dir = project_dir / "test_package"
        package_dir.mkdir()
        # Create non-Python files only
        (package_dir / "README.md").touch()

        # Act
        layout = detect_project_layout()

        # Assert - should fallback since no Python files
        assert layout.layout == ProjectLayout.UNKNOWN

    def test_detect_app_layout_no_python_files(self, project_dir: Path) -> None:
        """Test app layout when app dir exists but has no Python files."""
        # Arrange
        app_dir = project_dir / "app"
        app_dir.mkdir()
        # Create non-Python files only
        (app_dir / "config.json").touch()
        (project_dir / "pyproject.toml").touch()

        # Act
        layout = detect_project_layout()

        # Assert - should fallback since no Python files
        assert layout.layout == ProjectLayout.UNKNOWN

    def test_flat_layout_no_pyproject_toml(self, project_dir: Path) -> None:
        """Test flat layout detection when Python files exist but no pyproject.toml."""
        # Arrange
        (project_dir / "main.py").touch()
        (project_dir / "utils.py").touch()
        # No pyproject.toml

        # Act
        layout = detect_project_layout()

        # Assert - should fallback since no pyproject.toml
        assert layout.layout == ProjectLayout.UNKNOWN

    def test_apply_ty_config_with_existing_tool_section(self, project_dir: Path) -> None:
        """Test applying ty config when tool section already exists."""
        # Arrange
        pyproject_content = """
[project]
name = "test-project"
version = "0.1.0"

[tool]
[tool.ruff]
line-length = 88

[build-system]
requires = ["setuptools"]
"""
        (project_dir / "pyproject.toml").write_text(pyproject_content)

        layout = LayoutDetection(layout=ProjectLayout.SRC_LAYOUT, root_paths=["./src"], package_name="test_project")

        # Act
        apply_ty_config(layout)

        # Assert
        with open(project_dir / "pyproject.toml") as f:
            config = toml.load(f)

        assert "tool" in config
        assert "ruff" in config["tool"]  # Existing tool config preserved
        assert "ty" in config["tool"]  # New ty config added
        assert config["tool"]["ty"]["environment"]["root"] == ["./src"]
