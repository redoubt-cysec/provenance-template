# Quick Start: pipx

**Status:** ✅ Production Ready | **Test Coverage:** Phase 1 + Phase 2 | **Automated:** Yes

## Installation

### Install pipx First (if needed)

```bash
# macOS
brew install pipx
pipx ensurepath

# Linux (Ubuntu/Debian)
sudo apt install pipx
pipx ensurepath

# Linux (Fedora)
sudo dnf install pipx
pipx ensurepath

# Using pip (any platform)
pip install --user pipx
python3 -m pipx ensurepath
```

### Install provenance-demo

```bash
# Install latest version
pipx install provenance-demo

# Verify installation
provenance-demo --version
provenance-demo verify
```

### Install Specific Version

```bash
# Install specific version
pipx install provenance-demo==0.1.0

# Install from GitHub
pipx install git+https://github.com/redoubt-cysec/provenance-demo.git@v0.1.0
```

### Install with Extras

```bash
# Install with development dependencies
pipx install provenance-demo[dev]
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

echo "=== pipx Installation Validation ==="

# Check if pipx is installed
if ! command -v pipx &> /dev/null; then
    echo "❌ pipx not found"
    exit 1
fi
echo "✓ pipx found"

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

# Verify pipx shows the package
if ! pipx list | grep -q "provenance-demo"; then
    echo "❌ Package not in pipx list"
    exit 1
fi
echo "✓ Package registered with pipx"

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

Save as `validate-pipx.sh` and run:

```bash
chmod +x validate-pipx.sh
./validate-pipx.sh
```

## Upgrading

```bash
# Upgrade to latest version
pipx upgrade provenance-demo

# Upgrade all pipx packages
pipx upgrade-all

# Reinstall (clean upgrade)
pipx reinstall provenance-demo

# Verify new version
provenance-demo --version
```

## Uninstalling

```bash
# Uninstall the package
pipx uninstall provenance-demo

# Verify removal
! command -v provenance-demo && echo "Successfully uninstalled"

# Optional: Remove pipx data directory
rm -rf ~/.local/pipx/venvs/provenance-demo
```

## Troubleshooting

### pipx Command Not Found After Installation

**Problem:** `pipx: command not found` after installing pipx

**Solution:**
```bash
# Ensure PATH is set
pipx ensurepath

# Manually add to PATH (Linux/macOS)
export PATH="$HOME/.local/bin:$PATH"

# Add to shell profile
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Command Not Found After pipx install

**Problem:** `provenance-demo: command not found` after `pipx install`

**Solution:**
```bash
# Check if package is installed
pipx list

# Verify pipx bin directory is in PATH
echo $PATH | grep -o ~/.local/bin

# Reinstall with verbose output
pipx reinstall provenance-demo --verbose

# Manually add to PATH if needed
export PATH="$HOME/.local/bin:$PATH"
```

### Virtual Environment Issues

**Problem:** `Error: 'provenance-demo' already seems to be installed`

**Solution:**
```bash
# Force reinstall
pipx reinstall --force provenance-demo

# Or uninstall first
pipx uninstall provenance-demo
pipx install provenance-demo
```

### Python Version Mismatch

**Problem:** `requires Python >=3.10`

**Solution:**
```bash
# Check Python version used by pipx
pipx list --verbose

# Install with specific Python version
pipx install --python python3.11 provenance-demo

# Or set default Python
export PIPX_DEFAULT_PYTHON=python3.11
pipx install provenance-demo
```

### Verification Fails

**Problem:** Verification checks fail

**Solutions:**
1. **Missing tools:**
   ```bash
   # Install required tools
   brew install cosign gh osv-scanner  # macOS

   # Linux (Ubuntu/Debian)
   sudo apt install cosign gh osv-scanner
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

### Use pipx for CLI Tools

pipx is specifically designed for installing Python CLI applications in isolated environments:

```bash
# Each tool gets its own virtual environment
pipx install provenance-demo
pipx install black
pipx install pytest

# No conflicts between dependencies
pipx list
```

### Inject Dependencies

Add packages to an existing pipx environment:

```bash
# Install provenance-demo
pipx install provenance-demo

# Inject additional packages into the same environment
pipx inject provenance-demo pytest
pipx inject provenance-demo pyyaml
```

### Run Commands Without Installing

```bash
# Run once without installing
pipx run provenance-demo hello "World"

# Run specific version
pipx run provenance-demo==0.1.0 --version
```

### Regular Updates

```bash
# Check for updates
pipx list

# Upgrade all packages
pipx upgrade-all

# Set up automated updates (cron/systemd)
echo "0 0 * * 0 pipx upgrade-all" | crontab -
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
- Isolated environment integrity

## Platform-Specific Notes

### Linux

- Default install location: `~/.local/bin/`
- Virtual environments: `~/.local/pipx/venvs/`
- Configuration: `~/.local/pipx/`
- Works on all major distributions
- Best practice: Use system package manager for pipx

### macOS

- Default install location: `~/.local/bin/`
- Virtual environments: `~/.local/pipx/venvs/`
- Recommended: Install pipx via Homebrew
- Works on Intel and Apple Silicon
- May require Command Line Tools

### Windows

- Default install location: `%USERPROFILE%\.local\bin\`
- Virtual environments: `%USERPROFILE%\.local\pipx\venvs\`
- Add to PATH via System Properties
- Requires Python 3.10+
- PowerShell recommended over CMD

## Advantages of pipx

### Isolation

- Each CLI tool runs in its own virtual environment
- No dependency conflicts between tools
- System Python remains clean

### Convenience

- Commands available globally
- No need to activate virtual environments
- Automatic PATH management

### Safety

- No sudo/admin required
- User-level installation
- Easy to uninstall completely

### Performance

- Faster startup than Docker
- Native Python execution
- No container overhead

## Next Steps

1. ✅ Installation complete
2. ✅ Validation passed
3. ✅ Verification run
4. 📖 Read [Platform Support](../PLATFORM-SUPPORT.md) for other platforms
5. 📖 See [Verification Example](../../security/VERIFICATION-EXAMPLE.md) for details
6. 🚀 Start using the template for your CLI project
7. 💡 Explore `pipx run` for trying tools without installing

## Support

- **Issues:** Report pipx-specific issues at [GitHub Issues](https://github.com/redoubt-cysec/provenance-demo/issues)
- **Documentation:** See [Platform Status](../PLATFORM-STATUS.md) for complete details
- **Security:** Run `provenance-demo verify` for security validation
- **pipx Docs:** Visit [pipx.pypa.io](https://pipx.pypa.io)

---

**Installation Method:** pipx (Isolated Python Applications)
**Production Ready:** ✅ Yes
**Automated Testing:** ✅ Phase 1 + Phase 2
**Last Updated:** 2025-11-01
