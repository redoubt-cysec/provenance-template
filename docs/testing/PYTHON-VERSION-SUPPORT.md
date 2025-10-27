# Python Version Support

**Supported Python Versions**: 3.10, 3.11, 3.12, 3.13
**Testing Strategy**: Multi-version matrix testing in CI/CD
**Last Updated**: 2025-10-26

---

## Overview

This project supports Python 3.10 through 3.13, ensuring broad compatibility across:
- Ubuntu/Debian (APT repository)
- Fedora/RHEL (RPM repository)
- macOS (Homebrew)
- PyPI (pip install)
- Docker containers
- Universal packages (AppImage, Snap, Flatpak)

---

## Python Version Requirements

### Minimum Version: Python 3.10

```toml
# pyproject.toml
requires-python = ">=3.10"

classifiers = [
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Programming Language :: Python :: 3.13",
]
```

###  Version Support Matrix

| Python Version | Status | EOL Date | Notes |
|----------------|--------|----------|-------|
| 3.10 | ✅ Supported | October 2026 | Minimum version |
| 3.11 | ✅ Supported | October 2027 | |
| 3.12 | ✅ Supported | October 2028 | |
| 3.13 | ✅ Supported | October 2029 | Latest stable |
| 3.9 | ❌ Not supported | October 2025 | EOL soon |
| 3.14 | 🔮 Future | TBD | When released |

---

## Testing Infrastructure

### 1. Local Testing

Test all Python versions locally using VM infrastructure:

```bash
# Test all Python versions (3.10-3.13)
./scripts/phase2-testing/test-python-multiversion-vm.sh
```

This script will:
- Create Ubuntu 22.04 VMs for each Python version
- Install Python from deadsnakes PPA
- Test .pyz file execution
- Test package imports
- Verify all commands work correctly
- Cleanup VMs automatically

**Time**: ~10-15 minutes (4 VMs × 2-3 minutes each)

### 2. Unit Tests (Fast)

Run unit tests on specific Python version:

```bash
# Using current Python
python -m pytest tests/ -v

# Using specific version
python3.10 -m pytest tests/ -v
python3.11 -m pytest tests/ -v
python3.12 -m pytest tests/ -v
python3.13 -m pytest tests/ -v
```

### 3. GitHub Actions (Automated)

Two workflows test Python compatibility:

#### A. Python Compatibility Workflow
**File**: `.github/workflows/python-compatibility.yml`

Runs on every push/PR:
- **Unit tests**: Fast tests on all Python versions
- **VM integration tests**: Full VM-based tests on Ubuntu + macOS

```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12', '3.13']
    os: [ubuntu-latest, macos-latest]
```

#### B. PyPI Multi-Version Workflow
**File**: `.github/workflows/pypi-multiversion.yml`

Tests published packages from TestPyPI:
- Manual dispatch workflow
- Tests pip install on all Python versions
- Verifies package works after installation

---

## Platform-Specific Python Versions

### Ubuntu/Debian (APT)

| Ubuntu Version | Default Python | Python 3.10-3.13 |
|----------------|----------------|------------------|
| Ubuntu 22.04 LTS | 3.10 | ✅ Via deadsnakes PPA |
| Ubuntu 24.04 LTS | 3.12 | ✅ Via deadsnakes PPA |
| Debian 12 | 3.11 | ✅ Via deadsnakes PPA |

```bash
# Install specific version
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.10 python3.11 python3.12 python3.13
```

### Fedora/RHEL (RPM)

| Distribution | Default Python | Python 3.10-3.13 |
|--------------|----------------|------------------|
| Fedora 38 | 3.11 | ✅ |
| Fedora 39 | 3.12 | ✅ |
| RHEL 9 | 3.9 | ⚠️ Use Python 3.10+ |

```bash
# Install specific version
sudo dnf install python3.10 python3.11 python3.12 python3.13
```

### macOS (Homebrew)

```bash
# Install specific version
brew install python@3.10
brew install python@3.11
brew install python@3.12
brew install python@3.13
```

### PyPI (Universal)

```bash
# Install with pip (any Python 3.10+)
pip install demo-secure-cli

# Install for specific version
python3.10 -m pip install demo-secure-cli
python3.11 -m pip install demo-secure-cli
python3.12 -m pip install demo-secure-cli
python3.13 -m pip install demo-secure-cli
```

---

## Compatibility Guidelines

### Do's ✅

- **Use standard library features** available in Python 3.10+
- **Test on all supported versions** before release
- **Declare version in pyproject.toml** (`requires-python = ">=3.10"`)
- **Use uv for dependency management** (supports version pinning)
- **Avoid version-specific code** unless absolutely necessary

### Don'ts ❌

- **Don't use Python 3.11+ features** without version checks
- **Don't use deprecated features** (e.g., `collections.abc` vs `collections`)
- **Don't assume specific Python version** at runtime
- **Don't use `sys.version_info` checks** unless necessary

### Version-Specific Code (If Needed)

```python
import sys

if sys.version_info >= (3, 11):
    # Use Python 3.11+ feature
    import tomllib
else:
    # Fallback for Python 3.10
    import tomli as tomllib
```

---

## Dependency Management

### Using uv

```bash
# Install dependencies for all Python versions
uv pip install -e ".[dev]"

# Lock dependencies (respects requires-python)
uv lock

# Build for specific Python version
uv build --python 3.10
uv build --python 3.11
uv build --python 3.12
uv build --python 3.13
```

### Dependency Constraints

```toml
# pyproject.toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0",        # Compatible with Python 3.10+
    "pytest-cov>=4.0",    # Compatible with Python 3.10+
    "tomli; python_version<'3.11'",  # Conditional dependency
]
```

---

## Common Issues & Solutions

### Issue 1: ImportError on Python 3.10

**Problem**: Using Python 3.11+ stdlib features

```python
# ❌ Fails on Python 3.10
import tomllib

# ✅ Works on all versions
import sys
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
```

**Solution**: Add conditional imports or use backport packages

### Issue 2: Type Hints Not Working

**Problem**: Using modern type hints syntax

```python
# ❌ Fails on Python 3.10
def process(items: list[str]) -> dict[str, int]:
    ...

# ✅ Works on all versions
from typing import List, Dict

def process(items: List[str]) -> Dict[str, int]:
    ...
```

**Solution**: Use `typing` module instead of builtin types for generics (Python 3.9+)

### Issue 3: Package Build Fails

**Problem**: Missing Python version in build environment

```bash
# Check available versions
python --version
python3.10 --version
python3.11 --version

# Install missing versions (Ubuntu)
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.10 python3.11 python3.12 python3.13
```

---

## CI/CD Integration

### GitHub Actions Matrix

```yaml
jobs:
  test:
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12', '3.13']
        os: [ubuntu-latest, macos-latest, windows-latest]

    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Test
        run: python -m pytest tests/ -v
```

### Pre-Commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    hooks:
      - id: black
        language_version: python3.10  # Use minimum version

  - repo: https://github.com/pycqa/isort
    hooks:
      - id: isort
        language_version: python3.10
```

---

## Version Deprecation Policy

### When to Drop Support

Drop support for a Python version when:
1. **EOL reached**: Official end-of-life date passed
2. **Security risk**: No more security updates
3. **Low usage**: < 5% of users on that version
4. **Blocking features**: Need features from newer versions

### Deprecation Process

1. **Announce** (6 months before):
   - GitHub release notes
   - Documentation update
   - Warning in package metadata

2. **Warn** (3 months before):
   - Runtime warnings for deprecated versions
   - Update CI to mark as deprecated

3. **Remove** (0 months):
   - Update `requires-python` in pyproject.toml
   - Remove from CI matrix
   - Document in changelog

### Example Timeline

```
2025-10: Python 3.9 EOL announced
2026-04: Add runtime warnings
2026-07: Update requires-python to >=3.10
2026-10: Remove Python 3.9 from CI
```

---

## Monitoring & Maintenance

### Check Python Version Usage

```bash
# List all Python versions in CI
grep -r "python-version:" .github/workflows/

# Check requires-python
grep "requires-python" pyproject.toml

# List Python classifiers
grep "Programming Language :: Python" pyproject.toml
```

### Update Python Versions

```bash
# Update pyproject.toml
# 1. Update requires-python
# 2. Update classifiers
# 3. Update GitHub Actions workflows
# 4. Test with new versions
# 5. Update documentation
```

---

## References

- **Python Release Schedule**: https://peps.python.org/pep-0602/
- **Python EOL Dates**: https://devguide.python.org/versions/
- **deadsnakes PPA**: https://github.com/deadsnakes/python3.x
- **uv Documentation**: https://github.com/astral-sh/uv

---

**Last Updated**: 2025-10-26
**Next Review**: 2026-01 (or when Python 3.14 is released)
