# Quick Start: WinGet (Windows Package Manager)

**Status:** ✅ Configuration Ready | **Test Coverage:** Phase 1 | **Automated:** Partial

## Installation

### Install WinGet (if needed)

WinGet is pre-installed on Windows 11 and recent Windows 10 updates. If not available:

```powershell
# Install from Microsoft Store
# Search for "App Installer" and install/update

# Or download from GitHub
# https://github.com/microsoft/winget-cli/releases
```

### Install Provenance Demo

```powershell
# Install latest version
winget install redoubt-cysec.ProvenanceDemo

# Verify installation
provenance-demo --version
provenance-demo verify
```

### Install Specific Version

```powershell
# Install specific version
winget install redoubt-cysec.ProvenanceDemo --version 0.1.0

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
# Save as validate-winget.ps1
$ErrorActionPreference = 'Stop'

Write-Host "=== WinGet Installation Validation ==="

# Check if command exists
if (!(Get-Command provenance-demo -ErrorAction SilentlyContinue)) {
    Write-Host "❌ provenance-demo command not found"
    Write-Host "💡 Try restarting your terminal or adding to PATH"
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

Write-Host ""
Write-Host "✅ All validation checks passed!"
Write-Host "Installation is working correctly."
```

Run validation:

```powershell
powershell -ExecutionPolicy Bypass -File validate-winget.ps1
```

## Upgrading

```powershell
# Upgrade to latest version
winget upgrade redoubt-cysec.ProvenanceDemo

# Or specify version
winget upgrade redoubt-cysec.ProvenanceDemo --version 0.1.1

# Verify new version
provenance-demo --version
```

## Uninstalling

```powershell
# Uninstall package
winget uninstall redoubt-cysec.ProvenanceDemo

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
# Reload PATH environment variable
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Or restart PowerShell/Terminal

# Check installation path
winget list redoubt-cysec.ProvenanceDemo
```

### WinGet Not Found

**Problem:** `winget : The term 'winget' is not recognized`

**Solution:**
```powershell
# Install App Installer from Microsoft Store
# Or download from: https://github.com/microsoft/winget-cli/releases

# Verify WinGet installation
winget --version

# Update WinGet to latest version
# Open Microsoft Store > Library > Get updates > Update "App Installer"
```

### Package Not Found

**Problem:** `No package found matching input criteria`

**Solution:**
```powershell
# Update WinGet source
winget source update

# Search for package
winget search provenance-demo

# Use full package identifier
winget install redoubt-cysec.ProvenanceDemo
```

### Python Not Found

**Problem:** `Python is not installed` or Python version too old

**Solution:**
```powershell
# Check Python version
python --version

# Install Python via WinGet (if needed)
winget install Python.Python.3.11

# Verify Python installation
python --version
```

### Installation Requires Elevation

**Problem:** Installation requires administrator privileges

**Solution:**
```powershell
# Run Terminal/PowerShell as Administrator
# Right-click and select "Run as Administrator"

# Then retry installation
winget install redoubt-cysec.ProvenanceDemo
```

### Verification Fails

**Problem:** Verification checks fail

**Solutions:**
1. **Missing tools:**
   ```powershell
   # Install required tools
   winget install GitHub.cli

   # For cosign and osv-scanner, see official installation guides
   # cosign: https://docs.sigstore.dev/cosign/installation
   # osv-scanner: https://google.github.io/osv-scanner/installation
   ```

2. **Network issues:**
   ```powershell
   # Check connectivity
   Test-NetConnection -ComputerName api.github.com -Port 443

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

### Hash Mismatch Error

**Problem:** WinGet reports hash mismatch during installation

**Solution:**
```powershell
# This indicates the manifest has incorrect hash
# Report this issue to the package maintainers

# As a workaround, download directly from GitHub Releases
Invoke-WebRequest -Uri "https://github.com/redoubt-cysec/provenance-template/releases/download/v0.1.0/provenance-demo.pyz" -OutFile "provenance-demo.pyz"

# Verify checksum manually
gh release download v0.1.0 --repo redoubt-cysec/provenance-template --pattern 'checksums.txt'
Get-FileHash provenance-demo.pyz -Algorithm SHA256
Get-Content checksums.txt | Select-String "provenance-demo.pyz"
```

## Best Practices

### Pin Versions

```powershell
# Install specific version for reproducibility
winget install redoubt-cysec.ProvenanceDemo --version 0.1.0

# Document version in your environment setup scripts
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

### Use in CI/CD

WinGet can be used in GitHub Actions and other CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Install provenance-demo
  run: winget install redoubt-cysec.ProvenanceDemo --version 0.1.0

- name: Verify installation
  run: provenance-demo verify
  env:
    GITHUB_REPOSITORY: redoubt-cysec/provenance-template
```

## Platform-Specific Notes

### Windows 10

- Requires Windows 10 version 1809 or higher
- App Installer (WinGet) may need manual installation/update
- Works on both x64 and ARM64 architectures

### Windows 11

- WinGet is pre-installed
- May need to update App Installer for latest features
- Full support for all WinGet features

### Windows Server

- WinGet is not installed by default on Windows Server
- Can be installed manually from GitHub releases
- Tested on Windows Server 2019 and 2022

## Security Verification

### Verify Package Manifest

WinGet manifests are submitted to microsoft/winget-pkgs repository:

```powershell
# View package manifest
winget show redoubt-cysec.ProvenanceDemo

# Check package source
winget source list
```

### Verify Installation Integrity

```powershell
# Download checksum file
gh release download v0.1.0 --repo redoubt-cysec/provenance-template --pattern 'checksums.txt'

# Get installed file location
$installPath = (Get-Command provenance-demo).Source

# Verify hash
Get-FileHash $installPath -Algorithm SHA256
Get-Content checksums.txt | Select-String "provenance-demo.pyz"
```

### Check for Updates

```powershell
# Check if updates are available
winget upgrade redoubt-cysec.ProvenanceDemo
```

## Advanced Usage

### Export Installed Packages

```powershell
# Export all installed packages
winget export -o packages.json

# This includes provenance-demo with its version
# Can be used for environment replication
```

### Import Package Configuration

```powershell
# Install packages from exported configuration
winget import -i packages.json
```

### Silent Installation

```powershell
# Install without prompts (for automation)
winget install redoubt-cysec.ProvenanceDemo --silent

# Or
winget install redoubt-cysec.ProvenanceDemo -h
```

## Next Steps

1. ✅ Installation complete
2. ✅ Validation passed
3. ✅ Verification run
4. 📖 Read [Platform Support](../PLATFORM-SUPPORT.md) for other platforms
5. 📖 See [Verification Example](../../security/VERIFICATION-EXAMPLE.md) for details
6. 🚀 Start using the template for your CLI project

## Support

- **Issues:** Report WinGet-specific issues at [GitHub Issues](https://github.com/redoubt-cysec/provenance-demo/issues)
- **Documentation:** See [Platform Status](../PLATFORM-STATUS.md) for complete details
- **Security:** Run `provenance-demo verify` for security validation
- **WinGet Help:** Visit [docs.microsoft.com/windows/package-manager/winget](https://docs.microsoft.com/windows/package-manager/winget)
- **WinGet Community:** [github.com/microsoft/winget-cli](https://github.com/microsoft/winget-cli)

---

**Installation Method:** WinGet (Windows Package Manager)
**Production Ready:** ⏳ Configuration Ready (Publishing Pending)
**Automated Testing:** ✅ Phase 1
**Last Updated:** 2025-11-01
