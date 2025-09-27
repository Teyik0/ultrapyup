# Ultrapyup

**The AI-ready Python toolkit that helps you build and ship code _faster_.**

Ultrapyup is a zero-config Python development framework that provides a robust development experience for your team and your AI integrations. Built on modern Python tooling for lightning-fast performance, it automatically handles project setup, dependency management, and code quality without interrupting your workflow.

<div>
    <img src="https://img.shields.io/github/actions/workflow/status/teyik0/ultrapyup/cd.yaml?branch=main" alt="CD Status" />
    <img src="https://img.shields.io/pypi/v/ultrapyup" alt="PyPI Version" />
    <img src="https://img.shields.io/github/license/teyik0/ultrapyup" alt="License" />
    <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python Version" />
</div>

Heavily inspired by [Ultracite](https://github.com/haydenbleasel/ultracite), but built for the Python ecosystem.

## Quick Start

Install and initialize Ultrapyup in your project:

```sh
uvx ultrapyup
```

That's it! Ultrapyup will automatically detect your project structure and set up modern Python tooling with best practices. No configuration required.

## Key Features (Coming Soon)

### 🎯 **Zero-Config by Design**
Preconfigured rules optimized for Python projects with sensible defaults. Customize when needed, but it works perfectly out of the box.

### 🛡️ **Maximum Code Quality**
Enforces strict type checking with ty, code formatting with ruff, and testing best practices by default, catching errors and maintaining consistency before they become problems.

<!--### 🏗️ **Monorepo Ready**
Unified toolchain configuration across all packages and services, eliminating thousands of lines of duplicate config files while maintaining consistency.-->

### 🤖 **AI-Friendly**
Ensures consistent code style and quality across all team members and AI models, eliminating debates over formatting and reducing code review friction. Supports GitHub Copilot, Cursor, Windsurf, Zed, Claude Code, and OpenAI Codex.

### 🔧 **Intuitive and Robust**
Automatically manages dependencies, handles virtual environments, and enforces code quality standards with clear error reporting for issues that need manual attention.

## How It Works (Planned)

- **Automatic project detection** and intelligent setup
- **Dependency management** with blazing-fast uv (Rust-powered)
- **Code formatting** with ruff (Rust-powered)
- **Type safety** enforced with strict ty rules (Rust-powered)
- **Import organization** and cleanup

## Why Ultrapyup?

Finally a lightning-fast Python toolkit that ensures you, your team, and your AI agents are writing code in harmony. Stop spending time on tooling configuration and dependency management. Let Ultrapyup handle the mundane so you can focus on building and shipping.

Inspired by the success of [Ultracite](https://www.ultracite.ai/) in the JavaScript ecosystem, Ultrapyup brings the same philosophy to the Python ecosystem.

## Development

This project uses uv for dependency management and packaging. To contribute:

```bash
# Clone the repository
git clone https://github.com/teyik0/ultrapyup.git
cd ultrapyup

# Install dependencies
uv sync --all-extras --dev

# Setup pre-commit
uv run lefthook install

# Run tests
uv run pytest -n auto tests --cov --cov-report=xml --cov-report=term

# Run code quality checks
uv run ruff check . --fix
uv run ty check .

# Format code
uv run ruff format .
```

## Contributing

We're in early development and welcome contributions! Whether it's:
- 🐛 Bug reports and fixes
- 💡 Feature suggestions and implementations
- 📚 Documentation improvements
- 🧪 Testing and feedback

Please open an issue or submit a PR. Check our [contributing guidelines](.github/CONTRIBUTING.md) for more details.

---

**Star this repo** if you're excited about faster Python development! Follow the project for updates as we build toward a stable release.
