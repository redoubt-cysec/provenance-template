# Quick Start: Homebrew

**Status:** ✅ Production Ready | **Test Coverage:** Phase 1 + Phase 2 | **Automated:** Yes

## Installation

### Install Homebrew (if needed)

```bash
# macOS or Linux
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Follow post-install instructions to add to PATH
```

### Install provenance-demo

```bash
# Add tap (if using custom tap)
brew tap redoubt-cysec/tap

# Install latest version
brew install provenance-demo

# Verify installation
provenance-demo --version
provenance-demo verify
```

### Install Specific Version

```bash
# Install specific version
brew install provenance-demo@0.1.0

# Or pin current version
brew pin provenance-demo

# Unpin when ready to upgrade
brew unpin provenance-demo
```

## Verification

After installation, run comprehensive verification:

```bash
# Set your repository
export GITHUB_REPOSITORY=redoubt-cysec/provenance-template

# Download release artifacts for verification
gh release download v0.0.1-alpha.40 --repo $GITHUB_REPOSITORY

# Run 14-check verification
provenance-demo verify

# Expected: ✓ 14/14 checks passed
```

### Verify Homebrew Installation

```bash
# Check installation info
brew info provenance-demo

# Verify formula
brew audit provenance-demo

# Check dependencies
brew deps provenance-demo

# Verify binary location
which provenance-demo
```

## Validation Script

Quick validation that everything works:

```bash
#!/bin/bash
set -e

echo "=== Homebrew Installation Validation ==="

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found"
    exit 1
fi
echo "✓ Homebrew found"

# Check if package is installed
if ! brew list provenance-demo &> /dev/null; then
    echo "❌ provenance-demo not installed via Homebrew"
    exit 1
fi
echo "✓ Package installed via Homebrew"

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

# Verify installation path
INSTALL_PATH=$(brew --prefix provenance-demo)
if [[ ! -d "$INSTALL_PATH" ]]; then
    echo "❌ Installation directory not found"
    exit 1
fi
echo "✓ Installed at: $INSTALL_PATH"

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

# Verify no issues
ISSUES=$(brew doctor 2>&1 | grep -i provenance-demo || true)
if [[ -n "$ISSUES" ]]; then
    echo "⚠️  Homebrew doctor found issues:"
    echo "$ISSUES"
fi

echo ""
echo "✅ All validation checks passed!"
echo "Installation is working correctly."
```

Save as `validate-homebrew.sh` and run:

```bash
chmod +x validate-homebrew.sh
./validate-homebrew.sh
```

## Upgrading

```bash
# Update Homebrew formulae
brew update

# Upgrade provenance-demo
brew upgrade provenance-demo

# Or upgrade all packages
brew upgrade

# Verify new version
provenance-demo --version

# Clean up old versions
brew cleanup provenance-demo
```

## Uninstalling

```bash
# Uninstall the package
brew uninstall provenance-demo

# Remove tap (if added)
brew untap redoubt-cysec/tap

# Clean up all cached files
brew cleanup -s

# Verify removal
! command -v provenance-demo && echo "Successfully uninstalled"
```

## Troubleshooting

### Homebrew Not Found

**Problem:** `brew: command not found`

**Solution:**
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add to PATH (macOS Intel)
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/usr/local/bin/brew shellenv)"

# Add to PATH (macOS Apple Silicon)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# Add to PATH (Linux)
echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
```

### Formula Not Found

**Problem:** `Error: No available formula with the name "provenance-demo"`

**Solution:**
```bash
# Update Homebrew
brew update

# Add custom tap
brew tap redoubt-cysec/tap

# Search for formula
brew search provenance-demo

# If using core formula
brew install provenance-demo
```

### Outdated Dependencies

**Problem:** `Error: A newer Command Line Tools release is available`

**Solution:**
```bash
# macOS: Update Command Line Tools
softwareupdate --all --install --force

# Or reinstall
xcode-select --install

# Linux: Update build tools
sudo apt update && sudo apt upgrade  # Ubuntu/Debian
sudo dnf update  # Fedora
```

### Permissions Error

**Problem:** `Permission denied` errors during installation

**Solution:**
```bash
# Fix Homebrew permissions (macOS)
sudo chown -R $(whoami) $(brew --prefix)/*

# Fix Homebrew permissions (Linux)
sudo chown -R $USER /home/linuxbrew/.linuxbrew

# Run brew doctor to check for issues
brew doctor
```

### Conflicting Versions

**Problem:** Multiple installations or version conflicts

**Solution:**
```bash
# Unlink all versions
brew unlink provenance-demo

# Link specific version
brew link provenance-demo

# Or force link
brew link --overwrite provenance-demo

# Check which version is active
which provenance-demo
provenance-demo --version
```

### Installation Fails

**Problem:** Installation fails during build or download

**Solution:**
```bash
# Clean Homebrew cache
brew cleanup -s

# Remove cached downloads
rm -rf "$(brew --cache)"

# Retry installation with verbose output
brew install --verbose --debug provenance-demo

# Check for system issues
brew doctor
```

## Best Practices

### Keep Homebrew Updated

```bash
# Regular maintenance routine
brew update          # Update formulae
brew upgrade         # Upgrade packages
brew cleanup         # Remove old versions
brew doctor          # Check for issues

# Automate with cron (run weekly)
cat > ~/brew-maintenance.sh << 'EOF'
#!/bin/bash
brew update
brew upgrade
brew cleanup
brew doctor
EOF
chmod +x ~/brew-maintenance.sh
```

### Pin Critical Versions

```bash
# Pin version to prevent upgrades
brew pin provenance-demo

# List pinned packages
brew list --pinned

# Unpin when ready
brew unpin provenance-demo
```

### Use brew bundle

```bash
# Create Brewfile
cat > Brewfile << 'EOF'
tap "redoubt-cysec/tap"
brew "provenance-demo"
brew "cosign"
brew "gh"
brew "osv-scanner"
EOF

# Install all from Brewfile
brew bundle install

# Keep Brewfile in version control
git add Brewfile
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
- Proper Homebrew integration

## Platform-Specific Notes

### macOS Intel (x86_64)

- Install location: `/usr/local/Cellar/provenance-demo/`
- Binary location: `/usr/local/bin/provenance-demo`
- Homebrew prefix: `/usr/local`
- Requires macOS 10.15 (Catalina) or newer

### macOS Apple Silicon (arm64)

- Install location: `/opt/homebrew/Cellar/provenance-demo/`
- Binary location: `/opt/homebrew/bin/provenance-demo`
- Homebrew prefix: `/opt/homebrew`
- Requires macOS 11.0 (Big Sur) or newer
- Native ARM64 support

### Linux (Homebrew on Linux)

- Install location: `/home/linuxbrew/.linuxbrew/Cellar/provenance-demo/`
- Binary location: `/home/linuxbrew/.linuxbrew/bin/provenance-demo`
- Homebrew prefix: `/home/linuxbrew/.linuxbrew`
- Requires build tools (gcc, make, etc.)
- Works on Ubuntu, Debian, Fedora, CentOS, etc.

## Homebrew Advantages

### Package Management

- Automatic dependency resolution
- Easy updates and rollbacks
- Clean uninstallation
- Version management

### Integration

- System PATH integration
- Shell completion support
- Service management (via brew services)
- Cross-platform (macOS + Linux)

### Quality Assurance

- Formula auditing
- Automated testing
- Reproducible builds
- Community review

### Developer Friendly

- Easy to create custom taps
- Simple formula syntax
- Well-documented
- Large ecosystem

## Advanced Usage

### Create Custom Tap

```bash
# Create tap repository
mkdir -p homebrew-tap/Formula
cd homebrew-tap

# Create formula
cat > Formula/provenance-demo.rb << 'EOF'
class ProvenanceDemo < Formula
  desc "Minimal demo CLI with hardened release pipeline"
  homepage "https://github.com/redoubt-cysec/provenance-demo"
  url "https://github.com/redoubt-cysec/provenance-demo/archive/v0.1.0.tar.gz"
  sha256 "..."
  license "MIT"

  depends_on "python@3.11"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/provenance-demo --version")
  end
end
EOF

# Push to GitHub as username/homebrew-tap
# Users install with: brew install username/tap/provenance-demo
```

### Use Multiple Versions

```bash
# Install multiple versions
brew install provenance-demo
brew install provenance-demo@0.1.0

# Switch between versions
brew unlink provenance-demo && brew link provenance-demo@0.1.0
brew unlink provenance-demo@0.1.0 && brew link provenance-demo
```

## Next Steps

1. ✅ Installation complete
2. ✅ Validation passed
3. ✅ Verification run
4. 📖 Read [Platform Support](../PLATFORM-SUPPORT.md) for other platforms
5. 📖 See [Verification Example](../../security/VERIFICATION-EXAMPLE.md) for details
6. 🚀 Start using the template for your CLI project
7. 💡 Consider creating a Brewfile for reproducible setups
8. 🍺 Explore [Homebrew documentation](https://docs.brew.sh)

## Support

- **Issues:** Report Homebrew-specific issues at [GitHub Issues](https://github.com/redoubt-cysec/provenance-demo/issues)
- **Documentation:** See [Platform Status](../PLATFORM-STATUS.md) for complete details
- **Security:** Run `provenance-demo verify` for security validation
- **Homebrew:** Visit [brew.sh](https://brew.sh) for Homebrew documentation

---

**Installation Method:** Homebrew (macOS/Linux Package Manager)
**Production Ready:** ✅ Yes
**Automated Testing:** ✅ Phase 1 + Phase 2
**Last Updated:** 2025-11-01
