# Ultrapy Tests

Comprehensive test suite for the Ultrapy project initialization tool.

## Running Tests

### Run all tests
```bash
uv run pytest
```

### Run with verbose output
```bash
uv run pytest -v
```

### Run a specific test file
```bash
uv run pytest tests/test_initialize.py
```

### Run a specific test class
```bash
uv run pytest tests/test_initialize.py::TestCheckPythonProject
```

### Run a specific test
```bash
uv run pytest tests/test_initialize.py::TestCheckPythonProject::test_no_python_project
```

### Run with coverage

#### Basic Coverage Report
```bash
uv run pytest --cov=ultrapy
```

#### Coverage with Missing Lines
```bash
uv run pytest --cov=ultrapy --cov-report=term-missing
```

#### HTML Coverage Report (Visual)
```bash
uv run pytest --cov=ultrapy --cov-report=html
# Open htmlcov/index.html in browser to view
```

#### XML Coverage Report (for CI/CD)
```bash
uv run pytest --cov=ultrapy --cov-report=xml
```

#### JSON Coverage Report
```bash
uv run pytest --cov=ultrapy --cov-report=json
```

#### Multiple Reports at Once
```bash
uv run pytest --cov=ultrapy --cov-report=term-missing --cov-report=html
```

#### Fail if Coverage Below Threshold
```bash
uv run pytest --cov=ultrapy --cov-fail-under=80
```

#### Coverage for Specific Module
```bash
uv run pytest --cov=ultrapy.utils tests/test_utils.py
```

#### Branch Coverage (More Detailed)
```bash
uv run pytest --cov=ultrapy --cov-branch
```

## Coverage Report Interpretation

- **Green lines**: Executed by tests
- **Red lines**: NOT covered by tests
- **Yellow lines**: Partially covered branches (if statements, etc.)

### Current Coverage Goals
- Maintain minimum 80% overall coverage
- 100% coverage for critical modules (initialize, package_manager)
- Focus on testing error paths and edge cases

## Test Structure

```
tests/
├── conftest.py          # Shared fixtures and test configuration
├── test_initialize.py   # Tests for project initialization
├── test_package_manager.py  # Tests for package manager detection and setup
└── test_utils.py        # Tests for utility functions
```

## Test Philosophy

### No Mocking of File System
- Tests use real temporary directories
- File operations are performed on actual files
- This ensures tests reflect real-world behavior

### Fixtures

Key fixtures in `conftest.py`:

- `temp_dir`: Creates a temporary directory for testing
- `project_dir`: Creates a temp directory and changes to it
- `python_project`: Creates a Python project with `uv init`
- `python_project_with_venv`: Creates a project with just `.venv`
- `project_with_requirements`: Creates a project with `requirements.txt`
- `project_with_pyproject`: Creates a project with `pyproject.toml`
- `project_with_ruff_config`: Creates a project with existing Ruff configuration
- `empty_project`: Creates an empty directory (no Python project)

## Test Coverage

### Initialize Module (`test_initialize.py`)
- **Project Detection**: Verifies Python project detection logic
- **Requirements Migration**: Tests migration from `requirements.txt` to `pyproject.toml`
- **Full Initialization Flow**: Tests complete setup with all options

### Package Manager Module (`test_package_manager.py`)
- **Auto-detection**: Tests automatic detection of package managers
- **Manual Selection**: Tests user selection when no lockfile exists
- **Dependency Installation**: Tests installation of dev dependencies
- **Ruff Configuration**: Tests Ruff config setup and overriding

### Utils Module (`test_utils.py`)
- **File Existence**: Tests file and directory existence checking
- **Logging**: Tests log output formatting and levels
- **Console Output**: Tests Rich console integration
- **Integration**: Tests combining multiple utilities

## Test Patterns

### Testing with Real Files
```python
def test_file_operations(temp_dir: Path):
    """Test with real file operations."""
    test_file = temp_dir / "test.txt"
    test_file.write_text("content")

    assert test_file.exists()
    assert test_file.read_text() == "content"
```

### Testing CLI Output
```python
def test_output(capsys):
    """Test console output."""
    log.info("Test message")

    captured = capsys.readouterr()
    assert "Test message" in captured.out
```

### Testing Project Initialization
```python
def test_with_project(python_project: Path):
    """Test with a real Python project."""
    # python_project fixture creates a real project with uv init
    assert (python_project / "pyproject.toml").exists()
```

## Adding New Tests

1. Create test functions starting with `test_`
2. Use descriptive names that explain what's being tested
3. Use fixtures for common setup
4. Test both success and failure cases
5. Use real files and directories, not mocks
6. Add docstrings explaining the test purpose

## Continuous Integration

Tests are automatically run on:
- Every commit (via pre-commit hooks)
- Pull requests
- Main branch pushes

## Common Issues

### Permission Errors
Some tests create/modify files. Ensure you have write permissions in the temp directory.

### Platform Differences
File system behavior may vary between Windows, macOS, and Linux. Tests should handle platform differences gracefully.

### Cleanup
Tests automatically clean up temporary directories. If cleanup fails, temp files may accumulate in your system's temp directory.
