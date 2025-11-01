# Quick Start: Scoop (Windows Command-Line Installer)

**Status:** ✅ Configuration Ready | **Test Coverage:** Phase 1 | **Automated:** Partial

## Installation

### Install Scoop (if needed)

```powershell
# Run in PowerShell (no admin rights needed!)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
```

### Add Provenance Demo Bucket

```powershell
# Add the custom bucket (after publishing)
scoop bucket add redoubt-cysec https://github.com/redoubt-cysec/scoop-bucket

# Or install directly from manifest URL
scoop install https://raw.githubusercontent.com/redoubt-cysec/provenance-template/main/packaging/scoop/provenance-demo.json
```

### Install Provenance Demo

```powershell
# Install latest version
scoop install provenance-demo

# Verify installation
provenance-demo --version
provenance-demo verify
```

### Install Specific Version

```powershell
# Install specific version
scoop install provenance-demo@0.1.0

# Verify installation
provenance-demo --version
```

## Verification

After installation, run comprehensive verification:

```powershell
# Set your repository
$env:GITHUB_REPOSITORY = "redoubt-cysec/provenance-template"

# Download release artifacts for verification
gh release download v0.1.0 --repo $env:GITHUB_REPOSITORY

# Run 14-check verification
provenance-demo verify

# Expected: ✓ 14/14 checks passed
```

## Validation Script

Quick validation that everything works:

```powershell
# Save as validate-scoop.ps1
$ErrorActionPreference = 'Stop'

Write-Host "=== Scoop Installation Validation ==="

# Check if command exists
if (!(Get-Command provenance-demo -ErrorAction SilentlyContinue)) {
    Write-Host "❌ provenance-demo command not found"
    Write-Host "💡 Try: scoop reset provenance-demo"
    exit 1
}
Write-Host "✓ Command found"

# Check version
$version = provenance-demo --version 2>&1
if ([string]::IsNullOrEmpty($version)) {
    Write-Host "❌ Version check failed"
    exit 1
}
Write-Host "✓ Version: $version"

# Test basic functionality
$output = provenance-demo hello "Test" 2>&1
if ($output -notlike "*Hello, Test*") {
    Write-Host "❌ Basic functionality test failed"
    exit 1
}
Write-Host "✓ Basic functionality works"

# Check if verify command exists
$verifyHelp = provenance-demo verify --help 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Verify command not available"
    exit 1
}
Write-Host "✓ Verify command available"

# Check Scoop manifest
$manifest = scoop info provenance-demo 2>&1
if ($manifest -match "provenance-demo") {
    Write-Host "✓ Scoop manifest valid"
} else {
    Write-Host "⚠️  Could not verify Scoop manifest"
}

Write-Host ""
Write-Host "✅ All validation checks passed!"
Write-Host "Installation is working correctly."
```

Run validation:

```powershell
powershell -ExecutionPolicy Bypass -File validate-scoop.ps1
```

## Upgrading

```powershell
# Update all apps
scoop update *

# Or update specific app
scoop update provenance-demo

# Verify new version
provenance-demo --version
```

## Uninstalling

```powershell
# Uninstall package
scoop uninstall provenance-demo

# Cleanup cache
scoop cache rm provenance-demo

# Verify removal
if (Get-Command provenance-demo -ErrorAction SilentlyContinue) {
    Write-Host "❌ Package not fully uninstalled"
} else {
    Write-Host "✅ Successfully uninstalled"
}
```

## Troubleshooting

### Command Not Found After Installation

**Problem:** `provenance-demo: command not found` or command not recognized

**Solution:**
```powershell
# Reset shims (Scoop's PATH management)
scoop reset provenance-demo

# Or reset all apps
scoop reset *

# Check installation
scoop list provenance-demo
```

### Scoop Not Found

**Problem:** `scoop : The term 'scoop' is not recognized`

**Solution:**
```powershell
# Install Scoop
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression

# Verify Scoop installation
scoop --version

# Update Scoop
scoop update
```

### Python Not Found

**Problem:** `Python is not installed` or Python version too old

**Solution:**
```powershell
# Check Python version
python --version

# Install Python via Scoop (if needed)
scoop install python

# Verify Python installation
python --version
```

### Bucket Not Found

**Problem:** `Could not find bucket`

**Solution:**
```powershell
# List available buckets
scoop bucket list

# Add the required bucket
scoop bucket add redoubt-cysec https://github.com/redoubt-cysec/scoop-bucket

# Or install directly from manifest URL
scoop install https://raw.githubusercontent.com/redoubt-cysec/provenance-template/main/packaging/scoop/provenance-demo.json
```

### Hash Mismatch Error

**Problem:** `Hash mismatch` during installation

**Solution:**
```powershell
# Skip hash check (not recommended for security)
scoop install provenance-demo --skip

# Or report the issue and wait for manifest update

# Verify integrity manually
gh release download v0.1.0 --repo redoubt-cysec/provenance-template --pattern 'checksums.txt'
Get-FileHash "$HOME\scoop\apps\provenance-demo\current\provenance-demo.pyz" -Algorithm SHA256
Get-Content checksums.txt | Select-String "provenance-demo.pyz"
```

### Verification Fails

**Problem:** Verification checks fail

**Solutions:**
1. **Missing tools:**
   ```powershell
   # Install required tools via Scoop
   scoop install gh

   # For cosign and osv-scanner, see official installation guides
   # cosign: https://docs.sigstore.dev/cosign/installation
   # osv-scanner: https://google.github.io/osv-scanner/installation
   ```

2. **Network issues:**
   ```powershell
   # Check connectivity
   Test-NetConnection -ComputerName api.github.com -Port 443

   # Configure proxy if needed
   scoop config proxy [username:password@]host:port

   # Retry verification
   provenance-demo verify --verbose
   ```

3. **Missing release artifacts:**
   ```powershell
   # Download all artifacts first
   $env:GITHUB_REPOSITORY = "redoubt-cysec/provenance-template"
   gh release download v0.1.0 --repo $env:GITHUB_REPOSITORY
   cd v0.1.0/
   provenance-demo verify
   ```

### Shim Conflicts

**Problem:** Command conflicts with another installed application

**Solution:**
```powershell
# List all shims
scoop list

# Check for conflicts
scoop which provenance-demo

# Reset the specific app
scoop reset provenance-demo
```

## Best Practices

### Use Scoop for Isolated Installations

Scoop installs apps in your user directory (`$HOME\scoop`), avoiding:
- Administrator privileges
- System PATH pollution
- Conflicts with system-wide installations

### Keep Apps Updated

```powershell
# Update Scoop itself
scoop update

# Update all installed apps
scoop update *

# Or update selectively
scoop update provenance-demo
```

### Verify After Installation

Always run verification after installing:

```powershell
provenance-demo verify
```

This ensures:
- Correct installation
- No tampering
- All security checks pass

### Use Status Command

```powershell
# Check for outdated apps
scoop status

# Shows which apps need updates
```

## Platform-Specific Notes

### Windows 10/11

- No administrator privileges required (user-space installation)
- Requires PowerShell 5.0 or higher
- Works on both x64 and ARM64 architectures (if Python supports it)

### Scoop Directory Structure

```
$HOME\scoop\
├── apps\               # Installed applications
│   └── provenance-demo\
│       ├── current\    # Symlink to latest version
│       └── 0.1.0\      # Specific version
├── shims\              # Command-line shortcuts (in PATH)
│   └── provenance-demo.exe
├── cache\              # Downloaded installers
└── persist\            # Persistent data across updates
```

### Portable Installation

Scoop installations are portable:

```powershell
# Copy entire scoop directory to another machine
# (same OS/architecture)
robocopy $HOME\scoop D:\portable\scoop /E

# Update paths on target machine
scoop reset *
```

## Security Verification

### Verify Manifest Integrity

```powershell
# View app manifest
scoop cat provenance-demo

# Check hash in manifest
$manifest = Get-Content "$HOME\scoop\apps\provenance-demo\current\manifest.json" | ConvertFrom-Json
Write-Host "Expected hash: $($manifest.hash)"

# Compare with actual file
$actualHash = Get-FileHash "$HOME\scoop\apps\provenance-demo\current\provenance-demo.pyz" -Algorithm SHA256
Write-Host "Actual hash: $($actualHash.Hash)"
```

### Verify Installation Source

```powershell
# Check which bucket installed the app
scoop info provenance-demo

# List configured buckets
scoop bucket list
```

## Advanced Usage

### Install from Local Manifest

```powershell
# Install from local JSON file
scoop install C:\path\to\provenance-demo.json
```

### Hold Version (Prevent Updates)

```powershell
# Hold specific version
scoop hold provenance-demo

# Check held apps
scoop list

# Unhold when ready to update
scoop unhold provenance-demo
```

### Export/Import Configuration

```powershell
# Export installed apps
scoop export > scoop-apps.txt

# Install on another machine
Get-Content scoop-apps.txt | ForEach-Object { scoop install $_ }
```

### Cleanup Old Versions

```powershell
# Remove old versions
scoop cleanup provenance-demo

# Remove all old versions
scoop cleanup *

# Show what would be cleaned
scoop cleanup * --preview
```

## Next Steps

1. ✅ Installation complete
2. ✅ Validation passed
3. ✅ Verification run
4. 📖 Read [Platform Support](../PLATFORM-SUPPORT.md) for other platforms
5. 📖 See [Verification Example](../../security/VERIFICATION-EXAMPLE.md) for details
6. 🚀 Start using the template for your CLI project

## Support

- **Issues:** Report Scoop-specific issues at [GitHub Issues](https://github.com/redoubt-cysec/provenance-demo/issues)
- **Documentation:** See [Platform Status](../PLATFORM-STATUS.md) for complete details
- **Security:** Run `provenance-demo verify` for security validation
- **Scoop Help:** Visit [scoop.sh](https://scoop.sh) and [github.com/ScoopInstaller/Scoop](https://github.com/ScoopInstaller/Scoop)
- **Scoop Wiki:** [github.com/ScoopInstaller/Scoop/wiki](https://github.com/ScoopInstaller/Scoop/wiki)

---

**Installation Method:** Scoop (Windows Command-Line Installer)
**Production Ready:** ⏳ Configuration Ready (Publishing Pending)
**Automated Testing:** ✅ Phase 1
**Last Updated:** 2025-11-01
