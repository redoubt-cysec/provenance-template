# Contributing to Redoubt Release Template

First off, thank you for considering contributing! Your help is greatly appreciated.

This document provides guidelines for contributing to this project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [How to Contribute](#how-to-contribute)
   - [Reporting Bugs](#reporting-bugs)
   - [Suggesting Enhancements](#suggesting-enhancements)
   - [Your First Code Contribution](#your-first-code-contribution)
   - [Pull Requests](#pull-requests)
3. [Development Setup](#development-setup)
4. [Style Guides](#style-guides)
   - [Git Commit Messages](#git-commit-messages)
   - [Python Style Guide](#python-style-guide)
5. [Testing](#testing)
6. [Releasing](#releasing)

## Code of Conduct

This project and everyone participating in it is governed by the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue. Include as much detail as possible:

- A clear and descriptive title.
- A step-by-step description of how to reproduce the bug.
- The expected behavior and what happened instead.
- Your operating system, Python version, and other relevant environment details.

### Suggesting Enhancements

If you have an idea for an enhancement, please open an issue. Include:

- A clear and descriptive title.
- A detailed explanation of the enhancement and why it would be useful.
- Any alternative solutions or features you've considered.

### Your First Code Contribution

Unsure where to begin? Look for issues tagged `good first issue`. These are a great way to get started.

### Pull Requests

1. Fork the repository and create your branch from `main`.
2. Set up your development environment (see [Development Setup](#development-setup)).
3. Make your changes.
4. Add or update tests for your changes.
5. Ensure all tests pass (`make test-all`).
6. Format your code (`make format`).
7. Lint your code (`make lint`).
8. Commit your changes using a descriptive commit message (see [Git Commit Messages](#git-commit-messages)).
9. Push your branch and open a pull request.

## Development Setup

We use a `Makefile` and a setup script to streamline the development process.

**Prerequisites:**

- Python 3.10+
- `uv` (recommended for virtual environment and package management)
- `git`

**One-Command Setup:**
To get your development environment ready, run:

```bash
make dev-setup
```

This will:

1. Create a Python virtual environment in `.venv/`.
2. Install all required dependencies.
3. Install pre-commit hooks.

**Manual Setup:**

```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
uv pip install -e ".[dev]"

# 3. Install pre-commit hooks
pre-commit install
```

**Common Commands:**

- `make install`: Install dependencies.
- `make test`: Run fast tests.
- `make test-all`: Run all tests.
- `make format`: Format code.
- `make lint`: Run linters.
- `make build`: Build the project.
- `make clean`: Clean build artifacts.

See the `Makefile` for a full list of commands.

## Style Guides

### Git Commit Messages

This project uses [Conventional Commits](https://www.conventionalcommits.org/). A commit message should be structured as follows:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Example:**

```
feat(cli): add a new 'status' command

The 'status' command provides information about the current configuration
and environment. This helps users diagnose issues more easily.
```

### Python Style Guide

We use [Ruff](https://github.com/charliermarsh/ruff) for formatting and linting. The configuration is in `pyproject.toml`.

- **Formatting:** `make format`
- **Linting:** `make lint`

We also use `mypy` for static type checking:

- **Type Checking:** `make type-check`

## Testing

We use `pytest` for testing.

- **Run fast tests:** `make test`
- **Run all tests (including slow ones):** `make test-all`
- **Run tests with coverage:** `make test-coverage`

New code should be accompanied by tests.

## Releasing

The release process is automated using GitHub Actions. When a new version tag (e.g., `v1.2.3`) is pushed to `main`, the release workflow will build and publish the packages.
