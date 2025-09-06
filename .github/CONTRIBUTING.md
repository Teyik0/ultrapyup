# Contributing to Ultrapyup

We're excited that you're interested in contributing to Ultrapyup! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) (mandatory)

### Setting Up Your Development Environment

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/<YOUR_USERNAME>/ultrapyup.git
   cd ultrapyup
   ```

2. **Create and switch to the dev branch**
   ```bash
   git checkout -b dev origin/dev
   ```

3. **Install dependencies**
   ```bash
   uv sync --all-extras --dev
   ```

4. **Set up pre-commit hooks**
   ```bash
   uv run lefthook install
   ```

5. **Verify your setup**
   ```bash
   uv run ruff check .
   uv run ty check .
   uv run pytest -n auto tests --cov --cov-report=xml --cov-report=term
   ```

## 🔄 Development Workflow

### Branch Strategy

We use a **dev-first workflow**:

- `main` - Stable releases only
- `dev` - Active development branch
- Feature branches are created from `dev` and merged back to `dev`

### Making Contributions

1. **Create a feature branch from dev**
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, concise code
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run tests
   uv run pytest -n auto tests --cov --cov-report=xml --cov-report=term

   # Check code quality
   uv run ruff check .
   uv run ty check .

   # Format code
   uv run ruff format .
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a PR targeting the `dev` branch (not `main`).

## 📝 Contribution Types

We welcome various types of contributions:

### 🐛 Bug Reports
- Use the GitHub issue template
- Include steps to reproduce
- Provide system information (OS, Python version, etc.)
- Include error messages and logs

### 💡 Feature Requests
- Describe the problem you're solving
- Explain your proposed solution
- Consider backward compatibility
- Discuss alternatives you've considered

### 🧪 Code Contributions
- Bug fixes
- New features
- Performance improvements
- Documentation updates
- Test improvements

### 📚 Documentation
- README improvements
- Code examples
- API documentation
- Tutorials and guides
