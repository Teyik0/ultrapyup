# Ultrapyup Resources

This directory contains base configurations that can be extended by projects using Ultrapyup. These configurations follow the "extend, don't replace" philosophy, similar to tools like Ultracite.

## 🎯 Available Configurations

### Ruff Configuration

**Configuration files:**
- `ruff_base.toml` - Base configuration (in installed ultrapyup library)
- `ruff.toml` - Project configuration template (created in user projects)

**How to extend:**

1. **Automatically during `ultrapyup init`:**
A `ruff.toml` file is automatically created in your project root that extends the base configuration from the installed ultrapyup library.

2. **Your generated `ruff.toml` will look like:**
```toml
# Ultrapyup Project Configuration
# This extends the base Ultrapyup configuration from the installed library

# Extend the base configuration from installed ultrapyup library
extend = "/path/to/installed/ultrapyup/resources/ruff_base.toml"

# Project-specific overrides
[lint]
extend-select = ["YOUR_ADDITIONAL_RULES"]
extend-ignore = ["RULES_TO_IGNORE"]

[lint.isort]
known-first-party = ["your_package_name"]
```

3. **Alternative: In your project's `pyproject.toml`:**
```toml
[tool.ruff]
extend = "/path/to/installed/ultrapyup/resources/ruff_base.toml"

# Project-specific settings
[tool.ruff.lint]
extend-select = ["D"]  # Add docstring rules

[tool.ruff.lint.pydocstyle]
convention = "numpy"   # Override to NumPy style
```

### Pre-commit Configurations

**Available files:**
- `lefthook.yaml` - Lefthook configuration
- `.pre-commit-config.yaml` - Pre-commit hooks configuration

**Usage:**
These are automatically copied to your project root during `ultrapyup init`.

## 🔧 Base Configuration Features

### Ruff Base Configuration Includes:

- **Modern Python standards** (Python 3.9+)
- **Black-compatible formatting** (88 char line length)
- **Comprehensive rule selection:**
  - `E`, `W` - pycodestyle errors and warnings
  - `F` - Pyflakes (unused imports, undefined names)
  - `UP` - pyupgrade (modernize Python code)
  - `B` - flake8-bugbear (catch likely bugs)
  - `SIM` - flake8-simplify (suggest simpler alternatives)
  - `I` - isort (import sorting)
  - `C4` - flake8-comprehensions (better comprehensions)
  - `PIE` - flake8-pie (misc linting rules)
  - `RET` - flake8-return (improve return statements)
  - `PERF` - Perflint (performance anti-patterns)
  - `RUF` - Ruff-specific rules

- **Smart ignores** for common issues
- **Per-file ignores** for tests and config files
- **Google-style docstrings** by default
- **Import organization** with isort
- **Complexity limits** (McCabe complexity ≤ 10)

## 🚀 Philosophy

### Extensible by Design

Like Ultracite for TypeScript/JavaScript, these configurations are designed to be:

1. **Zero-config by default** - Works out of the box
2. **Easily extensible** - Add rules without rewriting everything
3. **Project-specific** - Override only what you need
4. **Team-friendly** - Consistent across projects
5. **AI-compatible** - Clear, consistent code style

### Example Project Structure

```
your-project/
├── ruff.toml                # Extends ultrapyup base config (auto-created)
├── pyproject.toml           # Your project config
├── .pre-commit-config.yaml  # Copied from ultrapyup
└── src/
    └── your_package/
        └── __init__.py

### Your `ruff.toml` (auto-generated):
```toml
# Ultrapyup Project Configuration
extend = "/path/to/installed/ultrapyup/resources/ruff_base.toml"

[lint.isort]
known-first-party = ["your_package"]
```

## 🎨 Customization Examples

### Add strict type checking:
```toml
extend = "/path/to/installed/ultrapyup/resources/ruff_base.toml"

[lint]
extend-select = [
    "UP",   # More aggressive pyupgrade
    "ANN",  # Type annotations
    "S",    # Security rules
]
```

### For Django projects:
```toml
extend = "/path/to/installed/ultrapyup/resources/ruff_base.toml"

[lint]
extend-select = ["DJ"]  # Django-specific rules

[lint.per-file-ignores]
"*/migrations/*.py" = ["ALL"]  # Ignore migration files
```

### For FastAPI projects:
```toml
extend = "/path/to/installed/ultrapyup/resources/ruff_base.toml"

[lint]
extend-select = [
    "ASYNC",  # Async rules
    "DTZ",    # Datetime rules
]

[lint.isort]
known-first-party = ["app"]
```

## 📚 Learn More

- [Ruff Configuration Documentation](https://docs.astral.sh/ruff/configuration/)
- [Ruff Rules Reference](https://docs.astral.sh/ruff/rules/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Lefthook Documentation](https://github.com/evilmartians/lefthook)

## 🤝 Contributing

To improve these base configurations:

1. Test changes across multiple project types
2. Ensure backward compatibility
3. Document any breaking changes
4. Consider the impact on AI code generation tools
5. Follow the "extend, don't replace" philosophy
