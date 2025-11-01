# Quick Start: Snap

**Status:** ✅ Production Ready | **Test Coverage:** Phase 1 + Phase 2 | **Automated:** Yes

## Installation

### Install snapd (if needed)

```bash
# Ubuntu (usually pre-installed)
sudo apt update
sudo apt install snapd

# Fedora
sudo dnf install snapd
sudo ln -s /var/lib/snapd/snap /snap

# Arch Linux
sudo pacman -S snapd
sudo systemctl enable --now snapd.socket

# Debian
sudo apt install snapd
sudo snap install core
```

### Install provenance-demo

```bash
# Install latest stable version
sudo snap install provenance-demo

# Install from edge channel (latest)
sudo snap install provenance-demo --edge

# Install from candidate channel (pre-release)
sudo snap install provenance-demo --candidate

# Verify installation
provenance-demo --version
provenance-demo verify
```

### Install Specific Version

```bash
# Install specific revision
sudo snap install provenance-demo --revision=1

# Install from specific channel
sudo snap install provenance-demo --channel=stable
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

### Verify Snap Installation

```bash
# Check snap info
snap info provenance-demo

# List installed snaps
snap list | grep provenance-demo

# Check snap connections
snap connections provenance-demo

# Verify snap signature
snap known assertion-type=snap-declaration | grep provenance-demo
```

## Validation Script

Quick validation that everything works:

```bash
#!/bin/bash
set -e

echo "=== Snap Installation Validation ==="

# Check if snapd is running
if ! systemctl is-active --quiet snapd; then
    echo "❌ snapd service not running"
    echo "Run: sudo systemctl start snapd"
    exit 1
fi
echo "✓ snapd service running"

# Check if snap is installed
if ! snap list | grep -q provenance-demo; then
    echo "❌ provenance-demo snap not installed"
    exit 1
fi
echo "✓ Snap installed"

# Check command exists
if ! command -v provenance-demo &> /dev/null; then
    echo "❌ provenance-demo command not found"
    echo "Try: sudo snap alias provenance-demo.provenance-demo provenance-demo"
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

# Check snap info
CHANNEL=$(snap info provenance-demo | grep "tracking:" | awk '{print $2}')
echo "✓ Channel: $CHANNEL"

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

# Check confinement
CONFINEMENT=$(snap info provenance-demo | grep "confinement:" | awk '{print $2}')
echo "✓ Confinement: $CONFINEMENT"

# Check snap health
if ! snap warnings | grep -q "No warnings"; then
    echo "⚠️  Snap warnings present"
    snap warnings
fi

echo ""
echo "✅ All validation checks passed!"
echo "Installation is working correctly."
```

Save as `validate-snap.sh` and run:

```bash
chmod +x validate-snap.sh
./validate-snap.sh
```

## Upgrading

```bash
# Refresh to latest version
sudo snap refresh provenance-demo

# Refresh all snaps
sudo snap refresh

# Switch channel (e.g., stable to edge)
sudo snap refresh provenance-demo --channel=edge

# Verify new version
provenance-demo --version

# Check update history
snap changes
```

## Uninstalling

```bash
# Uninstall the snap
sudo snap remove provenance-demo

# Remove including saved data
sudo snap remove --purge provenance-demo

# Verify removal
! command -v provenance-demo && echo "Successfully uninstalled"

# Check for remaining data
ls ~/snap/provenance-demo/
```

## Troubleshooting

### snapd Not Running

**Problem:** `snapd service is not running`

**Solution:**
```bash
# Start snapd
sudo systemctl start snapd

# Enable snapd to start on boot
sudo systemctl enable snapd

# Check status
sudo systemctl status snapd

# Restart if needed
sudo systemctl restart snapd
```

### Command Not Found After Installation

**Problem:** `provenance-demo: command not found`

**Solution:**
```bash
# Check if /snap/bin is in PATH
echo $PATH | grep /snap/bin

# Add to PATH
export PATH="/snap/bin:$PATH"

# Add to shell profile
echo 'export PATH="/snap/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Or create alias
sudo snap alias provenance-demo.provenance-demo provenance-demo

# Or use full snap command
snap run provenance-demo
```

### Permission Denied

**Problem:** `Permission denied` errors

**Solution:**
```bash
# Check snap confinement
snap info provenance-demo | grep confinement

# Grant additional permissions (if needed)
sudo snap connect provenance-demo:home
sudo snap connect provenance-demo:network

# List available interfaces
snap interface

# Check current connections
snap connections provenance-demo
```

### Installation Failed

**Problem:** Snap installation fails

**Solution:**
```bash
# Update snapd
sudo snap refresh snapd

# Clear snap cache
sudo rm -rf /var/lib/snapd/cache/*

# Retry installation
sudo snap install provenance-demo --verbose

# Check system logs
sudo journalctl -u snapd
```

### Outdated Version

**Problem:** Snap not updating to latest version

**Solution:**
```bash
# Force refresh
sudo snap refresh provenance-demo

# Check for updates
snap refresh --list

# Change update frequency
sudo snap set system refresh.timer=02:00-05:00

# Manual update check
sudo snap refresh
```

### Confinement Issues

**Problem:** App can't access certain files or resources

**Solution:**
```bash
# Check confinement status
snap info provenance-demo | grep confinement

# If strict confinement, check interfaces
snap connections provenance-demo

# Connect needed interfaces
sudo snap connect provenance-demo:home
sudo snap connect provenance-demo:network
sudo snap connect provenance-demo:removable-media

# Or install with --devmode (not recommended for production)
sudo snap install provenance-demo --devmode
```

## Best Practices

### Use Stable Channel

```bash
# Install from stable (recommended)
sudo snap install provenance-demo --stable

# Only use edge for testing
sudo snap install provenance-demo --edge

# Track stable channel
sudo snap refresh provenance-demo --channel=stable
```

### Enable Automatic Updates

```bash
# Snap updates automatically by default
# Check refresh timer
snap get system refresh.timer

# Customize refresh schedule (e.g., 2-5 AM)
sudo snap set system refresh.timer=02:00-05:00

# Disable automatic refresh (not recommended)
sudo snap set system refresh.timer=

# Re-enable automatic refresh
sudo snap set system refresh.timer=
```

### Manage Snap Versions

```bash
# List installed revisions
snap list --all provenance-demo

# Revert to previous version
sudo snap revert provenance-demo

# Keep specific number of old revisions
sudo snap set system refresh.retain=2

# Remove old revisions manually
snap list --all provenance-demo
sudo snap remove --revision=1 provenance-demo
```

### Configure Snap Permissions

```bash
# View available interfaces
snap interface

# Connect interfaces as needed
sudo snap connect provenance-demo:home
sudo snap connect provenance-demo:network
sudo snap connect provenance-demo:system-observe

# Disconnect if not needed
sudo snap disconnect provenance-demo:removable-media
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
- Snap confinement working properly

## Platform-Specific Notes

### Ubuntu

- Snapd pre-installed on Ubuntu 16.04+
- Default snap directory: `/snap/`
- User data: `~/snap/provenance-demo/`
- Most popular snap platform

### Fedora

- Requires manual snapd installation
- Symbolic link needed: `/snap`
- SELinux considerations
- Works well after setup

### Arch Linux

- Install from AUR: `snapd`
- Enable socket: `systemctl enable --now snapd.socket`
- Create symlink manually
- Community support

### Debian

- Available in Debian 10+
- Install `snapd` package
- Requires core snap
- Good compatibility

### Other Distributions

- Most Linux distributions supported
- Check [Snapcraft.io](https://snapcraft.io/docs/installing-snapd) for instructions
- May require additional configuration
- systemd required

## Snap Advantages

### Automatic Updates

- Updates delivered automatically
- Rollback capability
- Delta updates (bandwidth efficient)
- Background installation

### Security

- Confined environment
- AppArmor/SELinux integration
- Signature verification
- Trusted publisher verification

### Portability

- Works across distributions
- Bundled dependencies
- Consistent behavior
- No dependency conflicts

### Distribution

- Snap Store integration
- Multiple channels (stable, candidate, beta, edge)
- Easy publishing
- Built-in metrics

## Snap Channels

### Stable

- Production-ready releases
- Recommended for most users
- Thoroughly tested
- Best stability

### Candidate

- Release candidates
- Pre-release testing
- Nearly stable
- Feature complete

### Beta

- Beta releases
- Active development
- New features
- May have bugs

### Edge

- Latest builds
- Cutting edge
- Unstable
- For developers/testers

## Next Steps

1. ✅ Installation complete
2. ✅ Validation passed
3. ✅ Verification run
4. 📖 Read [Platform Support](../PLATFORM-SUPPORT.md) for other platforms
5. 📖 See [Verification Example](../../security/VERIFICATION-EXAMPLE.md) for details
6. 🚀 Start using the template for your CLI project
7. 💡 Explore snap channels for updates
8. 📦 Visit [Snapcraft.io](https://snapcraft.io) for more snaps

## Support

- **Issues:** Report Snap-specific issues at [GitHub Issues](https://github.com/redoubt-cysec/provenance-demo/issues)
- **Documentation:** See [Platform Status](../PLATFORM-STATUS.md) for complete details
- **Security:** Run `provenance-demo verify` for security validation
- **Snap Help:** Visit [Snapcraft Forum](https://forum.snapcraft.io)

---

**Installation Method:** Snap (Universal Linux Package)
**Production Ready:** ✅ Yes
**Automated Testing:** ✅ Phase 1 + Phase 2
**Last Updated:** 2025-11-01
