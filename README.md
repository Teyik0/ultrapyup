# Ultrapyup

**The AI-ready Python toolkit that helps you build and ship code _faster_.**

Ultrapyup is a zero-config Python development framework that provides a robust development experience for your team and your AI integrations. Built on modern Python tooling for lightning-fast performance, it automatically handles project setup, dependency management, and code quality without interrupting your workflow.

> **⚠️ Early Development**: Ultrapyup is in active development. APIs may change and features are being added rapidly. We welcome feedback and contributions!

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
uvx ultrapyup init
```

That's it! Ultrapyup will automatically detect your project structure and set up modern Python tooling with best practices. No configuration required.

## Key Features (Coming Soon)

### ⚡ **Subsecond Performance**
Built on [uv](https://github.com/astral-sh/uv) for instant dependency resolution and project management. Package installations and virtual environment setup feel seamless without interrupting your workflow.

### 🎯 **Zero-Config by Design**
Preconfigured rules optimized for FastAPI, Django, and data science projects with sensible defaults. Customize when needed, but it works perfectly out of the box.

### 🛡️ **Maximum Code Quality**
Enforces strict type checking with ty, code formatting with ruff, and testing best practices by default, catching errors and maintaining consistency before they become problems.

### 🏗️ **Monorepo Ready**
Unified toolchain configuration across all packages and services, eliminating thousands of lines of duplicate config files while maintaining consistency.

### 🤖 **AI-Friendly**
Ensures consistent code style and quality across all team members and AI models, eliminating debates over formatting and reducing code review friction. Supports GitHub Copilot, Cursor, Windsurf, Zed, Claude Code, and OpenAI Codex.

### 🔧 **Intuitive and Robust**
Automatically manages dependencies, handles virtual environments, and enforces code quality standards with clear error reporting for issues that need manual attention.

## How It Works (Planned)

Once set up, Ultrapyup will run mostly in the background:

- **Automatic project detection** and intelligent setup
- **Dependency management** with blazing-fast uv
- **Code formatting** with ruff (Rust-powered)
- **Type safety** enforced with strict ty rules
- **Import organization** and cleanup
- **Testing framework** with pytest and coverage

Because uv and ruff are extremely fast, even on large projects, running Ultrapyup's checks will be instantaneous and can comfortably run on every save without lag.

## Current Status

**✅ Available Now:**
- `ultrapyup init` - Project initialization and detection
- Basic project structure analysis
- Package manager detection (pip, uv, poetry, etc.)

**🚧 In Development:**
- Automated tooling setup (ruff, ty, pytest)
- Code quality enforcement
- AI-optimized configurations
- Plugin system for extensibility

**📋 Planned:**
- VS Code integration
- Pre-commit hooks setup
- CI/CD template generation
- Monorepo support

## Command Line Usage

```sh
# Initialize a new or existing Python project
uvx ultrapyup init

# Coming soon:
# ultrapyup format    - Format your code
# ultrapyup check     - Run quality checks
# ultrapyup test      - Run tests
# ultrapyup build     - Build your package
```

## Why Ultrapyup?

Finally — a lightning-fast Python toolkit that ensures you, your team, and your AI agents are writing code in harmony. Stop spending time on tooling configuration and dependency management. Let Ultrapyup handle the mundane so you can focus on building and shipping.

Inspired by the success of Ultracite in the JavaScript ecosystem, Ultrapyup brings the same philosophy to Python development.

## Development

This project uses uv for dependency management and packaging. To contribute:

```bash
# Clone the repository
git clone https://github.com/teyik0/ultrapyup.git
cd ultrapyup

# Install dependencies
uv sync --all-extras --dev

# Run tests
uv run pytest -n auto tests --cov

# Run code quality checks
uv run ruff check --output-format=github .
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

Please open an issue or submit a PR. Check our [contributing guidelines](CONTRIBUTING.md) for more details.

## Roadmap

- [ ] Complete core `init` command functionality
- [ ] Add automatic tooling configuration
- [ ] Implement code quality checks
- [ ] Add testing framework setup
- [ ] Create VS Code extension
- [ ] Build plugin ecosystem
- [ ] Add monorepo support

---

**Star this repo** if you're excited about faster Python development! Follow the project for updates as we build toward a stable release.
