# Quick Start: PyPI (pip/uv)

**Status:** ✅ Production Ready | **Test Coverage:** Phase 1 + Phase 2 | **Automated:** Yes

## Installation

### Using pip (Standard)

```bash
# Install latest version
pip install provenance-demo

# Verify installation
provenance-demo --version
provenance-demo verify
```

### Using uv (Fast)

```bash
# Install latest version
uv pip install provenance-demo

# Verify installation
provenance-demo --version
provenance-demo verify
```

### Install Specific Version

```bash
# Using pip
pip install provenance-demo==0.1.0

# Using uv
uv pip install provenance-demo==0.1.0
```

## Verification

After installation, run comprehensive verification:

```bash
# Set your repository
export GITHUB_REPOSITORY=redoubt-cysec/provenance-template

# Download release artifacts for verification
gh release download v0.1.0 --repo $GITHUB_REPOSITORY

# Run 14-check verification
provenance-demo verify

# Expected: ✓ 14/14 checks passed
```

## Validation Script

Quick validation that everything works:

```bash
#!/bin/bash
set -e

echo "=== PyPI Installation Validation ==="

# Check command exists
if ! command -v provenance-demo &> /dev/null; then
    echo "❌ provenance-demo command not found"
    exit 1
fi
echo "✓ Command found"

# Check version
VERSION=$(provenance-demo --version 2>&1)
if [[ -z "$VERSION" ]]; then
    echo "❌ Version check failed"
    exit 1
fi
echo "✓ Version: $VERSION"

# Test basic functionality
OUTPUT=$(provenance-demo hello "Test" 2>&1)
if [[ "$OUTPUT" != *"Hello, Test"* ]]; then
    echo "❌ Basic functionality test failed"
    exit 1
fi
echo "✓ Basic functionality works"

# Check if verify command exists
if ! provenance-demo verify --help &> /dev/null; then
    echo "❌ Verify command not available"
    exit 1
fi
echo "✓ Verify command available"

echo ""
echo "✅ All validation checks passed!"
echo "Installation is working correctly."
```

Save as `validate-pypi.sh` and run:

```bash
chmod +x validate-pypi.sh
./validate-pypi.sh
```

## Upgrading

```bash
# Using pip
pip install --upgrade provenance-demo

# Using uv
uv pip install --upgrade provenance-demo

# Verify new version
provenance-demo --version
```

## Uninstalling

```bash
# Using pip
pip uninstall provenance-demo

# Using uv
uv pip uninstall provenance-demo

# Verify removal
! command -v provenance-demo && echo "Successfully uninstalled"
```

## Troubleshooting

### Command Not Found After Installation

**Problem:** `provenance-demo: command not found`

**Solution:**
```bash
# Check if package is installed
pip list | grep provenance-demo

# Find where it was installed
python -m pip show provenance-demo

# Add Python scripts directory to PATH
export PATH="$HOME/.local/bin:$PATH"  # Linux/macOS
# or
export PATH="$PATH:$(python -m site --user-base)/bin"
```

### Permission Denied During Installation

**Problem:** `ERROR: Could not install packages due to an OSError: [Errno 13] Permission denied`

**Solution:**
```bash
# Install in user directory (recommended)
pip install --user provenance-demo

# Or use uv (handles this automatically)
uv pip install provenance-demo
```

### Wrong Python Version

**Problem:** `Requires Python >=3.11`

**Solution:**
```bash
# Check Python version
python --version

# Use specific Python version
python3.11 -m pip install provenance-demo

# Or use uv with specific Python
uv pip install --python 3.11 provenance-demo
```

### Verification Fails

**Problem:** Verification checks fail

**Solutions:**
1. **Missing tools:**
   ```bash
   # Install required tools
   brew install cosign gh osv-scanner  # macOS
   # Linux: See tool-specific docs
   ```

2. **Network issues:**
   ```bash
   # Check connectivity
   curl -I https://api.github.com

   # Retry verification
   provenance-demo verify --verbose
   ```

3. **Missing release artifacts:**
   ```bash
   # Download all artifacts first
   gh release download v0.1.0 --repo redoubt-cysec/provenance-template
   cd v0.1.0/
   export GITHUB_REPOSITORY=redoubt-cysec/provenance-template
   provenance-demo verify
   ```

## Best Practices

### Use Virtual Environments

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install in isolated environment
pip install provenance-demo
```

### Pin Versions in Requirements

```txt
# requirements.txt
provenance-demo==0.1.0
```

```bash
# Install from requirements
pip install -r requirements.txt
```

### Verify After Installation

Always run verification after installing:

```bash
provenance-demo verify
```

This ensures:
- Correct installation
- No tampering
- All security checks pass

## Platform-Specific Notes

### Linux
- Default install location: `~/.local/bin/`
- May need to add to PATH
- Works on all major distributions

### macOS
- Default install location: `/usr/local/bin/` or `~/Library/Python/3.x/bin/`
- May need to add to PATH
- Works on Intel and Apple Silicon

### Windows
- Default install location: `%APPDATA%\Python\Python3x\Scripts\`
- Add to PATH via System Properties
- Requires Python 3.11+

## Next Steps

1. ✅ Installation complete
2. ✅ Validation passed
3. ✅ Verification run
4. 📖 Read [Platform Support](../PLATFORM-SUPPORT.md) for other platforms
5. 📖 See [Verification Example](../../security/VERIFICATION-EXAMPLE.md) for details
6. 🚀 Start using the template for your CLI project

## Support

- **Issues:** Report PyPI-specific issues at [GitHub Issues](https://github.com/redoubt-cysec/provenance-demo/issues)
- **Documentation:** See [Platform Status](../PLATFORM-STATUS.md) for complete details
- **Security:** Run `provenance-demo verify` for security validation

---

**Installation Method:** PyPI (pip/uv)
**Production Ready:** ✅ Yes
**Automated Testing:** ✅ Phase 1 + Phase 2
**Last Updated:** 2025-11-01
