# Quick Start: Chocolatey (Windows)

**Status:** ✅ Configuration Ready | **Test Coverage:** Phase 1 | **Automated:** Partial

## Installation

### Install Chocolatey (if needed)

```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

### Install Provenance Demo

```powershell
# Install latest version
choco install provenance-demo

# Verify installation
provenance-demo --version
provenance-demo verify
```

### Install Specific Version

```powershell
# Install specific version
choco install provenance-demo --version=0.1.0

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
# Save as validate-chocolatey.ps1
$ErrorActionPreference = 'Stop'

Write-Host "=== Chocolatey Installation Validation ==="

# Check if command exists
if (!(Get-Command provenance-demo -ErrorAction SilentlyContinue)) {
    Write-Host "❌ provenance-demo command not found"
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
powershell -ExecutionPolicy Bypass -File validate-chocolatey.ps1
```

## Upgrading

```powershell
# Upgrade to latest version
choco upgrade provenance-demo

# Or upgrade specific version
choco upgrade provenance-demo --version=0.1.1

# Verify new version
provenance-demo --version
```

## Uninstalling

```powershell
# Uninstall package
choco uninstall provenance-demo

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

# Or restart PowerShell

# Check installation directory
choco list --local-only provenance-demo
```

### Permission Denied During Installation

**Problem:** `Access to the path is denied` or insufficient permissions

**Solution:**
```powershell
# Run PowerShell as Administrator
# Right-click PowerShell and select "Run as Administrator"

# Then retry installation
choco install provenance-demo
```

### Python Not Found

**Problem:** `Python is not installed` or Python version too old

**Solution:**
```powershell
# Check Python version
python --version

# Install Python via Chocolatey (if needed)
choco install python --version=3.11.0

# Verify Python installation
python --version
```

### Verification Fails

**Problem:** Verification checks fail

**Solutions:**
1. **Missing tools:**
   ```powershell
   # Install required tools via Chocolatey
   choco install gh

   # Or install manually from official sources
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

### Chocolatey Not Installed

**Problem:** `choco : The term 'choco' is not recognized`

**Solution:**
```powershell
# Install Chocolatey (run as Administrator)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Verify Chocolatey installation
choco --version
```

## Best Practices

### Pin Versions in Configuration

```powershell
# Create packages.config
@"
<?xml version="1.0" encoding="utf-8"?>
<packages>
  <package id="provenance-demo" version="0.1.0" />
</packages>
"@ | Out-File -FilePath packages.config -Encoding UTF8

# Install from configuration
choco install packages.config
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

### Use Offline Installation

For air-gapped environments:

```powershell
# Download package on connected machine
choco download provenance-demo

# Transfer .nupkg file to air-gapped machine

# Install offline
choco install provenance-demo.0.1.0.nupkg --source="."
```

## Platform-Specific Notes

### Windows 10/11

- Requires PowerShell 5.0 or higher
- Administrator privileges needed for installation
- Works on both x64 and ARM64 architectures
- Python 3.11+ required

### Windows Server

- Same requirements as Windows 10/11
- Tested on Windows Server 2019 and 2022
- May require enabling execution of PowerShell scripts

### Execution Policy

If you encounter execution policy issues:

```powershell
# Check current policy
Get-ExecutionPolicy

# Temporarily bypass for current session
Set-ExecutionPolicy Bypass -Scope Process

# Or set to RemoteSigned permanently (requires Admin)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Security Verification

### Verify Package Checksum

Chocolatey automatically verifies SHA256 checksums during installation. To manually verify:

```powershell
# Download checksum file
gh release download v0.1.0 --repo redoubt-cysec/provenance-template --pattern 'checksums.txt'

# Get installed file hash
Get-FileHash -Path "$env:ChocolateyInstall\lib\provenance-demo\tools\provenance-demo.pyz" -Algorithm SHA256

# Compare with checksums.txt
Get-Content checksums.txt | Select-String "provenance-demo.pyz"
```

### Verify Installation Source

```powershell
# Check package source
choco info provenance-demo

# Verify package is from official Chocolatey community repository
# Or from your configured private repository
```

## Next Steps

1. ✅ Installation complete
2. ✅ Validation passed
3. ✅ Verification run
4. 📖 Read [Platform Support](../PLATFORM-SUPPORT.md) for other platforms
5. 📖 See [Verification Example](../../security/VERIFICATION-EXAMPLE.md) for details
6. 🚀 Start using the template for your CLI project

## Support

- **Issues:** Report Chocolatey-specific issues at [GitHub Issues](https://github.com/redoubt-cysec/provenance-demo/issues)
- **Documentation:** See [Platform Status](../PLATFORM-STATUS.md) for complete details
- **Security:** Run `provenance-demo verify` for security validation
- **Chocolatey Help:** Visit [chocolatey.org/docs](https://docs.chocolatey.org)

---

**Installation Method:** Chocolatey (Windows Package Manager)
**Production Ready:** ⏳ Configuration Ready (Publishing Pending)
**Automated Testing:** ✅ Phase 1
**Last Updated:** 2025-11-01
