from ultrapyup.package_manager import PackageManager


# Code Style and Formatting Rules
code_style_rules = [
    "Use 4 spaces for indentation, never tabs.",
    "Limit line length to 120 characters maximum.",
    "Use double quotes for strings consistently.",
    "Add trailing commas in multi-line collections.",
    "Use lowercase with underscores for function and variable names (snake_case).",
    "Use PascalCase for class names.",
    "Use UPPER_SNAKE_CASE for constants.",
    "Place imports at the top of the file, after module docstrings.",
    "Group imports: standard library, third-party, local imports.",
    "Use absolute imports over relative imports when possible.",
    "Separate top-level function and class definitions with two blank lines.",
    "Separate method definitions inside classes with one blank line.",
    "End files with a single newline character.",
    "Remove trailing whitespace from all lines.",
    "Use spaces around operators and after commas.",
    "Don't use spaces inside parentheses, brackets, or braces.",
    "Use f-strings for string formatting instead of % or .format().",
    "Use single underscores for internal use, double underscores for name mangling.",
]

# Type Hints and Safety Rules
type_safety_rules = [
    "Add type hints to all function signatures and return types.",
    "Use type hints for class attributes and instance variables.",
    "Use T | None for parameters that can be None.",
    "Check for None explicitly when working with Optional types.",
    "Use type narrowing with isinstance() checks.",
    "Don't use Any type, alaways be specific.",
    "Use TypeVar for generic type parameters.",
    "Use Literal types for string enums and constants.",
    "Use Final for constants that shouldn't be reassigned.",
    "Use ClassVar for class variables shared across instances.",
    "Don't ignore type checker warnings without good reason.",
]

# Security Best Practices
security_rules = [
    "Never hardcode API keys, passwords, or secrets in source code.",
    "Use environment variables or secure credential management for secrets.",
    "Validate and sanitize all user inputs.",
    "Use parameterized queries to prevent SQL injection.",
    "Don't use eval(), exec(), or compile() with untrusted input.",
    "Don't use subprocess with shell=True for untrusted input.",
    "Use secure random number generation: secrets module over random.",
    "Set secure file permissions (avoid 777, use 644 or 600).",
    "Use HTTPS for all network communications.",
    "Validate file uploads and restrict file types.",
    "Use secure hashing algorithms (avoid MD5 and SHA1).",
    "Implement proper error handling without exposing sensitive information.",
    "Use cryptographic libraries properly (cryptography, not pycrypto).",
]

# Code Quality and Maintainability
quality_rules = [
    "Forbid the use of any try-except blocks in the code unless explicitly asked.",
    "Raise exceptions instead of returning error codes or null to crash the program fast.",
    "Keep functions small (less than 70 lines strict) and focused on a single responsibility.",
    "Use descriptive names for variables, functions, and classes.",
    "Write docstrings for all public modules, classes, and functions.",
    "Avoid deep nesting, use early returns instead.",
    "Don't repeat yourself (DRY principle).",
    "Use constants instead of magic numbers.",
    "Prefer composition over inheritance.",
    "Use context managers (with statements) for resource management.",
    "Don't use mutable default arguments in functions.",
    "Use enumerate() instead of range(len()) for indexing.",
    "Use zip() for parallel iteration over multiple sequences.",
    "Use list/dict/set comprehensions for simple transformations.",
    "Don't use comprehensions for complex logic, use regular loops.",
    "Use pathlib.Path instead of os.path for file operations.",
    "Put a limit on everything: all loops and queues must have bounds.",
    "Split compound conditions into simple nested if-else branches.",
    "State invariants positively, avoid negations in conditions.",
    "Declare variables at the smallest possible scope.",
    "Use explicit, descriptive names with units (e.g., timeout_ms, count_max).",
    "Order names by significance: most important words first.",
    "Make functions pure when possible, centralize state changes.",
    "Group related code with blank lines for visual organization.",
    "Use only simple, explicit control flow for maximum clarity.",
    "Comments explain WHY you wrote code this way, not WHAT it does.",
    "Code alone is not documentation - show your reasoning.",
    "Calculate variables close to where they are used (minimize POCPOU).",
    "Use simpler function signatures to reduce call-site complexity.",
    "Group resource allocation and deallocation with blank lines.",
    "Show intent explicitly - use precise functions over generic ones.",
    "Order matters for readability - put important things first.",
    "Don't abbreviate names unless for primitive counters or indexes.",
    "Use proper capitalization for acronyms and technical terms.",
    "Infuse names with meaning that reveals their purpose and lifetime.",
    "Choose related names with same character count for alignment.",
]

go_to_library_rules = [
    "Use itertools and functools for functional programming patterns.",
    "Use Pydantic for data validation and serialization.",
    "Use Typer for CLI application",
    "Use FastAPI for REST API",
]

# Error Handling and Robustness
error_handling_rules = [
    "Use if-else statements for expected conditions, never try-except.",
    "Log errors with appropriate detail and context.",
    "Validate function parameters at the beginning of functions.",
    "Validate all return values, and invariants..",
    "Use assertions for debugging, not for handling runtime errors.",
    "Handle edge cases explicitly (empty lists, None values, etc.).",
    "Use defensive programming: check inputs and preconditions.",
    "Fail fast: detect errors as early as possible.",
    "Provide meaningful error messages to users and developers.",
    "Assert both positive space (what you expect) and negative space (what you don't).",
    "Split compound assertions: prefer assert(a); assert(b); over assert(a and b).",
    "Use single-line if to assert implications: if condition: assert(expected).",
    "Assert compile-time constants and relationships for design integrity.",
    "Handle both valid data becoming invalid and invalid input gracefully.",
]

# Performance and Efficiency
performance_rules = [
    "Use built-in functions and data structures when possible.",
    "Use generators for large datasets to save memory.",
    "Use set operations for membership testing and deduplication.",
    "Use dict.get() instead of checking if key exists then accessing.",
    "Use collections.defaultdict for grouping operations.",
    "Use collections.Counter for counting operations.",
    "Profile code before optimizing (don't guess at bottlenecks).",
    "Use slots for classes with fixed attributes to save memory.",
    "Use functools.lru_cache for expensive function calls.",
    "Use itertools for memory-efficient iterator operations.",
    "Avoid creating unnecessary intermediate lists.",
    "Use string.join() for concatenating many strings.",
    "Use appropriate data structures (list vs set vs dict).",
    "Consider using NumPy for numerical computations.",
    "Use multiprocessing or threading for CPU/IO bound operations.",
]

# Testing Best Practices
testing_rules = [
    "Write tests for all public interfaces and functions.",
    "Use pytest as the testing framework.",
    "Use descriptive test function names (test_should_when_given).",
    "Follow AAA pattern: Arrange, Act, Assert.",
    "Use fixtures and conftest.py for test data and setup.",
    "Test edge cases and error conditions.",
    "Use parametrized tests for multiple input scenarios.",
    "Use temporary directories for file-based tests.",
    "Don't use sleep() in tests, use proper synchronization.",
    "Don't use mock and patch if not explicitly asked for.",
    "Test one thing per test function.",
    "Use assert statements, not assertEqual in pytest.",
    "Create assert helper function for redundant assertion across test.",
    "Write integration tests for critical user flows.",
    "Use code coverage tools but don't chase 100% coverage.",
    "Keep tests fast and independent.",
]

# Documentation Rules
documentation_rules = [
    "Don't write module-level docstrings explaining the module's purpose.",
    "Document all public classes, methods, and functions.",
    "Private/protected functions starting with _ don't need docstrings unless complex.",
    "Use Google-style docstrings with Args, Returns, and Raises sections.",
    "Include examples in docstrings for complex functions.",
    "Keep docstrings up to date with code changes.",
    "Use type hints instead of documenting types in docstrings.",
    "Write clear commit messages following conventional commits.",
    "Document environment variables and configuration options.",
    "Use meaningful variable names that reduce need for comments.",
    "Comment why, not what the code is doing.",
    "Update documentation when changing public APIs.",
]

# Package Management and Dependencies
dependency_rules = [
    "Use virtual environments for all projects.",
    "Keep requirements.txt or pyproject.toml up to date.",
    "Use development dependencies separately from production.",
    "Document system dependencies and Python version requirements.",
    "Use dependency injection instead of global imports when possible.",
    "Avoid circular imports between modules.",
    "Use __init__.py files to control package exports.",
    "Use entry points in setup.py/pyproject.toml for command-line tools.",
]

# Modern Python Features
modern_python_rules = [
    "Use dataclasses for simple data containers.",
    "Use async/await using anyo for I/O bound operations.",
    "Use match-case statements for complex conditionals (Python 3.10+).",
    "Use the walrus operator (:=) judiciously for readability.",
    "Use positional-only and keyword-only parameters when appropriate.",
    "Use Protocol for structural typing instead of ABC.",
    "Use functools.singledispatch for polymorphic functions.",
    "Use enum.Enum for constants with semantic meaning.",
    "Use typing.NamedTuple for simple immutable records.",
    "Use @property for computed attributes.",
    "Use __slots__ for memory-efficient classes.",
]

# Ruff-Specific Rules (Based on enabled rule codes)
ruff_rules = [
    "Fix import sorting issues (isort integration).",
    "Remove unused imports and variables.",
    "Fix pycodestyle errors (E4, E7, E9 series).",
    "Fix pyflakes errors (F series).",
    "Use pyupgrade suggestions for modern Python syntax.",
    "Follow flake8-bugbear recommendations (B series).",
    "Use flake8-simplify suggestions for cleaner code.",
    "Fix docstring issues following pydocstyle (D series).",
    "Handle datetime usage properly (flake8-datetimez).",
    "Fix argument and variable naming issues.",
    "Remove debugging statements (print, pdb).",
    "Fix security issues flagged by bandit (S series).",
    "Fix comprehension and generator issues.",
    "Remove redundant code and expressions.",
]

# Anti-Patterns to Avoid
antipattern_rules = [
    "Don't use wildcard imports (from module import *).",
    "Don't modify sys.path at runtime.",
    "Don't use global statements unless absolutely necessary, prefer function parameters.",
    "Don't use mutable objects as default parameters.",
    "Don't use == for singleton comparison (use 'is').",
    "Don't use len(sequence) == 0, use 'not sequence'.",
    "Don't use lambda for anything complex, define a function.",
    "Don't ignore return values from functions.",
    "Don't use exit() or quit() in modules (use sys.exit()).",
    "Don't use __import__() directly, use importlib.",
    "Don't use assert for data validation in production code.",
    "Don't use recursion without tail-call optimization consideration.",
    "Don't use recursion for bounded operations - prefer iterative solutions.",
    "Don't create abstractions without clear domain benefit.",
    "Don't duplicate variables or create aliases unnecessarily.",
    "Don't introduce variables before they are needed.",
    "Don't overload names with multiple context-dependent meanings.",
    "Don't rely on compiler/interpreter defaults - be explicit.",
    "Don't create compound conditions that are hard to verify.",
    "Don't leave code paths without bounds or termination guarantees.",
    "Don't trust external input without validation and bounds checking.",
    "Don't optimize before understanding the performance characteristics.",
    "Don't ignore the golden rule: assert positive AND negative space when testing.",
    "Don't use while loop",
    "Don't use try except block at all - raise exceptions to crash the program fast instead.",
]

common_commands = {
    "uv": [
        "`uvx ruff format .` - Format code automatically",
        "`uvx ruff check .` - Check for issues without fixing",
        "`uvx ruff check . --fix` - Check and fix issues automatically",
        "`uvx ty check .` - Run type checker",
        "`uv add <package>` - Add a package to the project",
        "`uv add --dev <package>` - Add a development package to the project",
        "`uv remove <package>` - Remove a package from the project",
        "`uv sync --all-groups` - Install all dependencies",
        "`uv run <script-name>.py` - Run a Python script within the virtual environment",
        "`uv run -m <module-name>` - Run a Python module within the virtual environment",
        "`uv run python` - Start an interactive Python REPL",
        "`uv build` - Build the project for distribution",
    ],
    "pip": [
        "`ruff format .` - Format code automatically",
        "`ruff check .` - Check for issues without fixing",
        "`ruff check . --fix` - Check and fix issues automatically",
        "`ty check .` - Run type checker",
        "`pip install <package>` - (then add manually to dependencies in pyproject.toml) Add a package to the project",
        "`pip install <package>` (then add manually to dependency-groups.dev in pyproject.toml) - Add a development package to the project",  # noqa: E501
        "`pip uninstall <package>` - (then remove accordingly from pyproject.toml) Remove a package from the project",
        '`pip install -e ".[dev]"` - Install all dependencies',
        "`python <script-name>.py` - Run a Python script within the virtual environment",
        "`python -m <module-name>` - Run a Python module within the virtual environment",
        "`python` - Start an interactive Python REPL",
    ],
    "poetry": [
        "`poetry run ruff format .` - Format code automatically",
        "`poetry run ruff check .` - Check for issues without fixing",
        "`poetry run ruff check . --fix` - Check and fix issues automatically",
        "`poetry run ty check .` - Run type checker",
        "`poetry add <package>` - Add a package to the project",
        "`poetry add --group dev <package>` - Add a development package to the project",
        "`poetry remove <package>` - Remove a package from the project",
        "`poetry install` - Install all dependencies",
        "`poetry run python <script-name>.py` - Run a Python script within the virtual environment",
        "`poetry run python -m <module-name>` - Run a Python module within the virtual environment",
        "`poetry run python` - Start an interactive Python REPL",
    ],
}


def get_rules_file(package_manager: PackageManager) -> str:
    """Generate rules file content for a specific package manager.

    Args:
        package_manager: Package manager to use ('uv', 'poetry', 'pip').
                        If None, auto-detect from project files.

    Returns:
        Complete rules file content as a string.
    """
    commands = common_commands.get(package_manager.value, common_commands["uv"])

    return _rules_template.format(
        code_style="\n".join(f"- {rule}" for rule in code_style_rules),
        type_safety="\n".join(f"- {rule}" for rule in type_safety_rules),
        security="\n".join(f"- {rule}" for rule in security_rules),
        quality="\n".join(f"- {rule}" for rule in quality_rules),
        library="\n".join(f"- {rule}" for rule in go_to_library_rules),
        error_handling="\n".join(f"- {rule}" for rule in error_handling_rules),
        performance="\n".join(f"- {rule}" for rule in performance_rules),
        testing="\n".join(f"- {rule}" for rule in testing_rules),
        documentation="\n".join(f"- {rule}" for rule in documentation_rules),
        dependency="\n".join(f"- {rule}" for rule in dependency_rules),
        modern_python="\n".join(f"- {rule}" for rule in modern_python_rules),
        ruff="\n".join(f"- {rule}" for rule in ruff_rules),
        antipattern="\n".join(f"- {rule}" for rule in antipattern_rules),
        common_commands="\n".join(f"- {cmd}" for cmd in commands),
    )


# Template for rules file content
_rules_template = """# Python AI Coding Rules and Best Practices

This document enforces strict code quality, security standards, and modern Python best practices
using Ruff's and Ty's lightning-fast linter, formatter and type checker.

## Key Principles
- Zero tolerance for security vulnerabilities
- Type safety with comprehensive type hints
- Performance-conscious development
- Maximum maintainability and readability
- AI-friendly and Human-friendly code generation patterns

## Before Writing Code
1. Analyze existing patterns in the codebase
2. Consider security implications and edge cases
3. Follow the rules below strictly
4. Validate with Ruff and Ty

## Rules Categories

### Code Style and Formatting
{code_style}

### Type Safety and Hints
{type_safety}

### Security Best Practices
{security}

### Code Quality and Maintainability
{quality}

### Go To Libraries
{library}

### Error Handling and Robustness
{error_handling}

### Performance and Efficiency
{performance}

### Testing Best Practices
{testing}

### Documentation Standards
{documentation}

### Package Management
{dependency}

### Modern Python Features
{modern_python}

### Ruff Linter Integration
{ruff}

### Anti-Patterns to Avoid
{antipattern}

## Common Commands
{common_commands}

## Example: Proper Function Definition
```python
# ✅ Good: Type hints, docstring, defensive programming, data validation
def calculate_average(numbers: list[float]) -> float | None:
    \"\"\"Calculate the arithmetic mean of a list of numbers.

    Args:
        numbers: List of numeric values to average.

    Returns:
        The arithmetic mean of the input numbers, or None if empty list.

    Raises:
        ValueError: If the input list is empty.
    \"\"\"
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")

    return sum(numbers) / len(numbers)

# ❌ Bad: No type hints, no docstring, poor error handling, no data validation
def calc_avg(nums):
    return sum(nums) / len(nums)
```

## Example: Security Best Practices
```python
# ✅ Good: Environment variables, parameterized queries
import os
import sqlite3
from typing import Optional

def get_user_by_id(user_id: int) -> Optional[dict]:
    \"\"\"Fetch user data by ID with proper security measures.\"\"\"
    db_path = os.getenv("DATABASE_PATH")
    if not db_path:
        msg = "DATABASE_PATH environment variable not set"
        raise ValueError(msg)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()

    return dict(result) if result else None

# ❌ Bad: Hardcoded paths, string formatting in queries
def get_user_bad(user_id: int):  # noqa: S608
    conn = sqlite3.connect("/path/to/db.sqlite")
    cursor = conn.cursor()
    # This example shows what NOT to do - SQL injection risk
    query = "SELECT * FROM users WHERE id = " + str(user_id)  # noqa: S608
    cursor.execute(query)  # noqa: S608
    return cursor.fetchone()
```
"""

# Combine all rules for backward compatibility
rules = [
    *code_style_rules,
    *type_safety_rules,
    *security_rules,
    *quality_rules,
    *error_handling_rules,
    *performance_rules,
    *testing_rules,
    *documentation_rules,
    *dependency_rules,
    *modern_python_rules,
    *ruff_rules,
    *antipattern_rules,
]
