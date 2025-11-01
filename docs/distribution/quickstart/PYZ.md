# Quick Start: Direct .pyz Execution

**Status:** ✅ Production Ready | **Test Coverage:** Phase 1 + Phase 2 | **Automated:** Yes

## Installation

### Download .pyz File

```bash
# Set version and repository
VERSION="v0.0.1-alpha.40"
REPO="redoubt-cysec/provenance-template"

# Download from GitHub Releases
gh release download $VERSION --repo $REPO --pattern "*.pyz"

# Or using curl
curl -LO "https://github.com/$REPO/releases/download/$VERSION/provenance-demo.pyz"

# Or using wget
wget "https://github.com/$REPO/releases/download/$VERSION/provenance-demo.pyz"
```

### Make Executable

```bash
# Add execute permissions
chmod +x provenance-demo.pyz

# Verify it works
./provenance-demo.pyz --version
./provenance-demo.pyz verify
```

### Optional: Add to PATH

```bash
# Move to user bin directory
mkdir -p ~/.local/bin
mv provenance-demo.pyz ~/.local/bin/provenance-demo

# Ensure PATH includes ~/.local/bin
export PATH="$HOME/.local/bin:$PATH"

# Add to shell profile for persistence
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Now use without ./ prefix
provenance-demo --version
```

## Verification

After download, verify the .pyz file:

```bash
# Set your repository
export GITHUB_REPOSITORY=redoubt-cysec/provenance-template

# Download all release artifacts for verification
gh release download v0.0.1-alpha.40 --repo $GITHUB_REPOSITORY

# Run 14-check verification
./provenance-demo.pyz verify

# Expected: ✓ 14/14 checks passed
```

### Verify File Integrity

```bash
# Check SHA256 hash
sha256sum provenance-demo.pyz

# Compare with release checksums
curl -sL "https://github.com/$REPO/releases/download/$VERSION/checksums.txt" | grep provenance-demo.pyz

# Verify Sigstore signature (if available)
cosign verify-blob \
  --signature provenance-demo.pyz.sig \
  --certificate provenance-demo.pyz.crt \
  --certificate-identity-regexp="https://github.com/$REPO" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com" \
  provenance-demo.pyz
```

## Validation Script

Quick validation that everything works:

```bash
#!/bin/bash
set -e

echo "=== .pyz Installation Validation ==="

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if [[ "$PYTHON_VERSION" < "3.10" ]]; then
    echo "❌ Python 3.10+ required (found: $PYTHON_VERSION)"
    exit 1
fi
echo "✓ Python version: $PYTHON_VERSION"

# Check if .pyz file exists
if [[ ! -f "provenance-demo.pyz" ]]; then
    echo "❌ provenance-demo.pyz not found in current directory"
    exit 1
fi
echo "✓ .pyz file found"

# Check if executable
if [[ ! -x "provenance-demo.pyz" ]]; then
    echo "❌ File is not executable"
    echo "Run: chmod +x provenance-demo.pyz"
    exit 1
fi
echo "✓ File is executable"

# Check version
VERSION=$(./provenance-demo.pyz --version 2>&1)
if [[ -z "$VERSION" ]]; then
    echo "❌ Version check failed"
    exit 1
fi
echo "✓ Version: $VERSION"

# Test basic functionality
OUTPUT=$(./provenance-demo.pyz hello "Test" 2>&1)
if [[ "$OUTPUT" != *"Hello, Test"* ]]; then
    echo "❌ Basic functionality test failed"
    exit 1
fi
echo "✓ Basic functionality works"

# Check if verify command exists
if ! ./provenance-demo.pyz verify --help &> /dev/null; then
    echo "❌ Verify command not available"
    exit 1
fi
echo "✓ Verify command available"

# Verify file integrity (if checksums.txt exists)
if [[ -f "checksums.txt" ]]; then
    EXPECTED=$(grep "provenance-demo.pyz" checksums.txt | awk '{print $1}')
    ACTUAL=$(sha256sum provenance-demo.pyz | awk '{print $1}')
    if [[ "$EXPECTED" != "$ACTUAL" ]]; then
        echo "❌ Checksum mismatch!"
        echo "Expected: $EXPECTED"
        echo "Actual: $ACTUAL"
        exit 1
    fi
    echo "✓ Checksum verified"
fi

echo ""
echo "✅ All validation checks passed!"
echo "Installation is working correctly."
```

Save as `validate-pyz.sh` and run:

```bash
chmod +x validate-pyz.sh
./validate-pyz.sh
```

## Upgrading

```bash
# Download new version
VERSION="v0.1.1"
REPO="redoubt-cysec/provenance-template"
gh release download $VERSION --repo $REPO --pattern "*.pyz"

# Backup old version (optional)
mv provenance-demo.pyz provenance-demo.pyz.old

# Replace with new version
mv provenance-demo-*.pyz provenance-demo.pyz
chmod +x provenance-demo.pyz

# Verify new version
./provenance-demo.pyz --version
```

## Uninstalling

```bash
# Remove the .pyz file
rm provenance-demo.pyz

# If installed to PATH
rm ~/.local/bin/provenance-demo

# Remove any backups
rm -f provenance-demo.pyz.old

# Verify removal
! command -v provenance-demo && echo "Successfully uninstalled"
```

## Troubleshooting

### Python Not Found

**Problem:** `/usr/bin/env: python3: No such file or directory`

**Solution:**
```bash
# Check if Python is installed
which python3

# Install Python (Ubuntu/Debian)
sudo apt install python3

# Install Python (macOS)
brew install python3

# Install Python (Fedora)
sudo dnf install python3

# Verify version
python3 --version
```

### Permission Denied

**Problem:** `Permission denied` when executing .pyz file

**Solution:**
```bash
# Add execute permission
chmod +x provenance-demo.pyz

# Or run with Python explicitly
python3 provenance-demo.pyz --version
```

### Wrong Python Version

**Problem:** `Requires Python >=3.10`

**Solution:**
```bash
# Check Python version
python3 --version

# Use specific Python version
python3.11 provenance-demo.pyz --version

# Create wrapper script with specific Python
cat > provenance-demo << 'EOF'
#!/bin/bash
python3.11 $(dirname "$0")/provenance-demo.pyz "$@"
EOF
chmod +x provenance-demo
```

### File Not Executable on Windows

**Problem:** `.pyz` files not directly executable on Windows

**Solution:**
```powershell
# Run with Python explicitly
python provenance-demo.pyz --version

# Or create batch wrapper
echo @python "%~dp0\provenance-demo.pyz" %* > provenance-demo.bat

# Use the wrapper
provenance-demo.bat --version
```

### Checksum Verification Failed

**Problem:** Downloaded file checksum doesn't match

**Solution:**
```bash
# Re-download the file
rm provenance-demo.pyz
gh release download $VERSION --repo $REPO --pattern "*.pyz"

# Verify download integrity
sha256sum provenance-demo.pyz

# Check release page for correct checksum
gh release view $VERSION --repo $REPO
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
   ./provenance-demo.pyz verify --verbose
   ```

3. **Missing release artifacts:**
   ```bash
   # Download all artifacts first
   gh release download v0.0.1-alpha.40 --repo redoubt-cysec/provenance-template
   ./provenance-demo.pyz verify
   ```

## Best Practices

### Verify Before Execution

Always verify the .pyz file before first use:

```bash
# Check SHA256
sha256sum provenance-demo.pyz

# Verify signature
cosign verify-blob provenance-demo.pyz \
  --signature provenance-demo.pyz.sig \
  --certificate provenance-demo.pyz.crt

# Run verification suite
./provenance-demo.pyz verify
```

### Use Specific Versions

Pin to specific release versions:

```bash
# Download specific version
VERSION="v0.1.0"
gh release download $VERSION --repo $REPO --pattern "*.pyz"

# Rename to include version
mv provenance-demo.pyz provenance-demo-0.1.0.pyz
```

### Create Wrapper Scripts

For easier usage across systems:

```bash
# Linux/macOS wrapper
cat > provenance-demo << 'EOF'
#!/bin/bash
exec python3 "$(dirname "$0")/provenance-demo.pyz" "$@"
EOF
chmod +x provenance-demo

# Windows wrapper (provenance-demo.bat)
@echo off
python "%~dp0\provenance-demo.pyz" %*
```

### Store Securely

Keep .pyz files in a safe location:

```bash
# Create dedicated directory
mkdir -p ~/bin/pyz-apps
mv provenance-demo.pyz ~/bin/pyz-apps/

# Add to PATH
export PATH="$HOME/bin/pyz-apps:$PATH"
```

## Platform-Specific Notes

### Linux

- Default Python location: `/usr/bin/python3`
- Works on all distributions with Python 3.10+
- Requires `python3` package
- Execute permissions required
- Shebang: `#!/usr/bin/env python3`

### macOS

- Default Python location: `/usr/bin/python3`
- Works on Intel and Apple Silicon
- May require Command Line Tools
- Quarantine may need removal: `xattr -d com.apple.quarantine provenance-demo.pyz`

### Windows

- Not directly executable (no shebang support)
- Must run as: `python provenance-demo.pyz`
- Or use `.bat` wrapper script
- Python must be in PATH
- Requires Python 3.10+ from python.org or Microsoft Store

## Advantages of .pyz Files

### Self-Contained

- Single file distribution
- No installation required
- All dependencies bundled
- Easy to transfer and share

### Portable

- Works on any system with Python
- No pip or package manager needed
- No virtual environment required
- Easy to version control

### Fast

- No network access required (after download)
- Instant startup
- No dependency resolution
- Direct Python execution

### Secure

- Verifiable with checksums
- Can be signed with Sigstore
- Immutable after creation
- Easy to audit

## Next Steps

1. ✅ Download complete
2. ✅ Validation passed
3. ✅ Verification run
4. 📖 Read [Platform Support](../PLATFORM-SUPPORT.md) for other platforms
5. 📖 See [Verification Example](../../security/VERIFICATION-EXAMPLE.md) for details
6. 🚀 Start using the template for your CLI project
7. 💡 Consider creating wrapper scripts for convenience

## Support

- **Issues:** Report .pyz-specific issues at [GitHub Issues](https://github.com/redoubt-cysec/provenance-demo/issues)
- **Documentation:** See [Platform Status](../PLATFORM-STATUS.md) for complete details
- **Security:** Run `./provenance-demo.pyz verify` for security validation
- **PEP 441:** Read [PEP 441 - Python .pyz Files](https://www.python.org/dev/peps/pep-0441/)

---

**Installation Method:** Direct .pyz Execution
**Production Ready:** ✅ Yes
**Automated Testing:** ✅ Phase 1 + Phase 2
**Last Updated:** 2025-11-01
