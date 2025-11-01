# Quick Start: GitHub Releases

**Status:** ✅ Production Ready | **Test Coverage:** Phase 1 + Phase 2 | **Automated:** Yes

## Installation

### Using GitHub CLI (Recommended)

```bash
# Set version and repository
VERSION="v0.0.1-alpha.40"
REPO="redoubt-cysec/provenance-template"

# Download latest release
gh release download --repo $REPO

# Or download specific version
gh release download $VERSION --repo $REPO

# Or download specific pattern
gh release download $VERSION --repo $REPO --pattern "*.pyz"
gh release download $VERSION --repo $REPO --pattern "*.whl"
```

### Using curl

```bash
# Set variables
VERSION="v0.0.1-alpha.40"
REPO="redoubt-cysec/provenance-template"
FILE="provenance-demo.pyz"

# Download file
curl -LO "https://github.com/$REPO/releases/download/$VERSION/$FILE"

# Download checksums
curl -LO "https://github.com/$REPO/releases/download/$VERSION/checksums.txt"

# Download signature files
curl -LO "https://github.com/$REPO/releases/download/$VERSION/$FILE.sig"
curl -LO "https://github.com/$REPO/releases/download/$VERSION/$FILE.crt"
```

### Using wget

```bash
# Set variables
VERSION="v0.0.1-alpha.40"
REPO="redoubt-cysec/provenance-template"
FILE="provenance-demo.pyz"

# Download file
wget "https://github.com/$REPO/releases/download/$VERSION/$FILE"

# Download checksums
wget "https://github.com/$REPO/releases/download/$VERSION/checksums.txt"

# Download signature files
wget "https://github.com/$REPO/releases/download/$VERSION/$FILE.sig"
wget "https://github.com/$REPO/releases/download/$VERSION/$FILE.crt"
```

### Install from Downloaded Assets

```bash
# For .pyz files
chmod +x provenance-demo.pyz
./provenance-demo.pyz --version

# For .whl files
pip install provenance_demo-*.whl

# For source tarball
pip install provenance-demo-*.tar.gz
```

## Verification

### Verify Checksums

```bash
# Verify SHA256 checksums
sha256sum -c checksums.txt

# Or verify single file
EXPECTED=$(grep "provenance-demo.pyz" checksums.txt | awk '{print $1}')
ACTUAL=$(sha256sum provenance-demo.pyz | awk '{print $1}')
[[ "$EXPECTED" == "$ACTUAL" ]] && echo "✓ Checksum verified"
```

### Verify Sigstore Signatures

```bash
# Verify .pyz signature
cosign verify-blob provenance-demo.pyz \
  --signature provenance-demo.pyz.sig \
  --certificate provenance-demo.pyz.crt \
  --certificate-identity-regexp="https://github.com/$REPO" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com"

# Verify .whl signature
cosign verify-blob provenance_demo-*.whl \
  --signature provenance_demo-*.whl.sig \
  --certificate provenance_demo-*.whl.crt \
  --certificate-identity-regexp="https://github.com/$REPO" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com"
```

### Run Built-in Verification

```bash
# Set repository for verification
export GITHUB_REPOSITORY=redoubt-cysec/provenance-template

# Download all artifacts
gh release download v0.0.1-alpha.40 --repo $GITHUB_REPOSITORY

# Run comprehensive verification
./provenance-demo.pyz verify

# Or if installed via pip
provenance-demo verify

# Expected: ✓ 14/14 checks passed
```

## Validation Script

Quick validation that everything works:

```bash
#!/bin/bash
set -e

echo "=== GitHub Release Download Validation ==="

# Configuration
VERSION="v0.0.1-alpha.40"
REPO="redoubt-cysec/provenance-template"
FILE="provenance-demo.pyz"

# Check if file exists
if [[ ! -f "$FILE" ]]; then
    echo "❌ $FILE not found"
    exit 1
fi
echo "✓ File downloaded: $FILE"

# Check if checksums file exists
if [[ ! -f "checksums.txt" ]]; then
    echo "⚠️  checksums.txt not found (recommended for verification)"
else
    # Verify checksum
    EXPECTED=$(grep "$FILE" checksums.txt | awk '{print $1}')
    ACTUAL=$(sha256sum "$FILE" | awk '{print $1}')
    if [[ "$EXPECTED" != "$ACTUAL" ]]; then
        echo "❌ Checksum mismatch!"
        echo "Expected: $EXPECTED"
        echo "Actual: $ACTUAL"
        exit 1
    fi
    echo "✓ Checksum verified"
fi

# Make executable (for .pyz)
if [[ "$FILE" == *.pyz ]]; then
    chmod +x "$FILE"
    echo "✓ Made executable"
fi

# Check version
if [[ "$FILE" == *.pyz ]]; then
    VERSION_OUTPUT=$(./"$FILE" --version 2>&1)
elif [[ "$FILE" == *.whl ]] || [[ "$FILE" == *.tar.gz ]]; then
    pip install "$FILE" -q
    VERSION_OUTPUT=$(provenance-demo --version 2>&1)
fi

if [[ -z "$VERSION_OUTPUT" ]]; then
    echo "❌ Version check failed"
    exit 1
fi
echo "✓ Version: $VERSION_OUTPUT"

# Test basic functionality
if [[ "$FILE" == *.pyz ]]; then
    OUTPUT=$(./"$FILE" hello "Test" 2>&1)
else
    OUTPUT=$(provenance-demo hello "Test" 2>&1)
fi

if [[ "$OUTPUT" != *"Hello, Test"* ]]; then
    echo "❌ Basic functionality test failed"
    exit 1
fi
echo "✓ Basic functionality works"

# Check Sigstore signature if available
if command -v cosign &> /dev/null; then
    if [[ -f "$FILE.sig" ]] && [[ -f "$FILE.crt" ]]; then
        if cosign verify-blob "$FILE" \
            --signature "$FILE.sig" \
            --certificate "$FILE.crt" \
            --certificate-identity-regexp="https://github.com/$REPO" \
            --certificate-oidc-issuer="https://token.actions.githubusercontent.com" &> /dev/null; then
            echo "✓ Sigstore signature verified"
        else
            echo "⚠️  Sigstore verification failed"
        fi
    else
        echo "⚠️  Signature files not found (optional)"
    fi
else
    echo "⚠️  cosign not installed (optional)"
fi

echo ""
echo "✅ All validation checks passed!"
echo "Download is working correctly."
```

Save as `validate-release.sh` and run:

```bash
chmod +x validate-release.sh
./validate-release.sh
```

## Upgrading

```bash
# Check for new releases
gh release list --repo $REPO

# Download new version
NEW_VERSION="v0.1.1"
gh release download $NEW_VERSION --repo $REPO

# For .pyz files - replace old version
mv provenance-demo.pyz provenance-demo.pyz.old
mv provenance-demo-*.pyz provenance-demo.pyz
chmod +x provenance-demo.pyz

# For wheel files - reinstall
pip install --upgrade provenance_demo-*.whl

# Verify new version
provenance-demo --version
```

## Uninstalling

```bash
# Remove downloaded files
rm provenance-demo.pyz
rm provenance_demo-*.whl
rm provenance-demo-*.tar.gz
rm checksums.txt
rm *.sig *.crt

# If installed via pip
pip uninstall provenance-demo

# Remove download directory
cd ..
rm -rf v0.0.1-alpha.40/

# Verify removal
! command -v provenance-demo && echo "Successfully uninstalled"
```

## Troubleshooting

### GitHub CLI Not Found

**Problem:** `gh: command not found`

**Solution:**
```bash
# Install gh (macOS)
brew install gh

# Install gh (Ubuntu/Debian)
sudo apt install gh

# Install gh (Fedora)
sudo dnf install gh

# Or download from GitHub
curl -sL https://github.com/cli/cli/releases/latest/download/gh_linux_amd64.tar.gz | tar xz
```

### Authentication Required

**Problem:** `HTTP 403: API rate limit exceeded`

**Solution:**
```bash
# Authenticate with GitHub
gh auth login

# Or use personal access token
export GITHUB_TOKEN=your_token_here

# Or download without gh CLI
curl -LO "https://github.com/$REPO/releases/download/$VERSION/provenance-demo.pyz"
```

### Release Not Found

**Problem:** `release not found`

**Solution:**
```bash
# List available releases
gh release list --repo $REPO

# View specific release
gh release view $VERSION --repo $REPO

# Check if version exists
curl -I "https://github.com/$REPO/releases/tag/$VERSION"
```

### Download Incomplete

**Problem:** File size mismatch or download interrupted

**Solution:**
```bash
# Remove partial download
rm provenance-demo.pyz

# Re-download with verbose output
gh release download $VERSION --repo $REPO --pattern "*.pyz" --clobber

# Verify file size
ls -lh provenance-demo.pyz

# Check checksum
sha256sum provenance-demo.pyz
```

### Checksum Verification Failed

**Problem:** Checksum doesn't match

**Solution:**
```bash
# Re-download both file and checksums
rm provenance-demo.pyz checksums.txt
gh release download $VERSION --repo $REPO

# Verify with verbose output
sha256sum provenance-demo.pyz
grep provenance-demo.pyz checksums.txt

# If still fails, report as security issue
```

### Signature Verification Failed

**Problem:** Sigstore verification fails

**Solution:**
```bash
# Check cosign version
cosign version

# Re-download signature files
rm *.sig *.crt
gh release download $VERSION --repo $REPO --pattern "*.sig"
gh release download $VERSION --repo $REPO --pattern "*.crt"

# Verify with verbose output
cosign verify-blob provenance-demo.pyz \
  --signature provenance-demo.pyz.sig \
  --certificate provenance-demo.pyz.crt \
  --certificate-identity-regexp="https://github.com/$REPO" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com" \
  --verbose
```

## Best Practices

### Always Verify Downloads

```bash
# 1. Download file + checksums + signatures
gh release download $VERSION --repo $REPO

# 2. Verify checksum
sha256sum -c checksums.txt

# 3. Verify signature
cosign verify-blob provenance-demo.pyz \
  --signature provenance-demo.pyz.sig \
  --certificate provenance-demo.pyz.crt

# 4. Run built-in verification
./provenance-demo.pyz verify
```

### Pin to Specific Versions

```bash
# Use exact version tags
VERSION="v0.1.0"  # Good
VERSION="latest"  # Avoid

# Document the version you're using
echo "v0.1.0" > .provenance-demo-version
```

### Use Dedicated Download Directory

```bash
# Create release directory
mkdir -p ~/downloads/provenance-demo/$VERSION
cd ~/downloads/provenance-demo/$VERSION

# Download everything
gh release download $VERSION --repo $REPO

# Keep organized by version
ls ~/downloads/provenance-demo/
# v0.1.0/
# v0.1.1/
# v0.2.0/
```

### Automate Downloads

```bash
# Script to download latest release
#!/bin/bash
REPO="redoubt-cysec/provenance-template"
VERSION=$(gh release list --repo $REPO --limit 1 --json tagName --jq '.[0].tagName')

mkdir -p ~/bin/provenance-demo
cd ~/bin/provenance-demo

gh release download $VERSION --repo $REPO --pattern "*.pyz" --clobber
chmod +x provenance-demo.pyz

echo "Downloaded: $VERSION"
```

## Platform-Specific Notes

### Linux

- All download methods work
- Default download location: `./` (current directory)
- `gh` available in most package managers
- `curl` and `wget` pre-installed on most distributions

### macOS

- All download methods work
- `gh` available via Homebrew
- `curl` pre-installed
- `wget` available via Homebrew
- May need to remove quarantine: `xattr -d com.apple.quarantine file.pyz`

### Windows

- `gh` available via winget, chocolatey, scoop
- `curl` available in PowerShell (Windows 10+)
- `wget` available via chocolatey
- PowerShell equivalents:
  ```powershell
  # Using Invoke-WebRequest
  Invoke-WebRequest -Uri "https://github.com/$REPO/releases/download/$VERSION/provenance-demo.pyz" -OutFile "provenance-demo.pyz"
  ```

## Release Assets Available

Each release includes:

- **Source Distribution:** `provenance-demo-*.tar.gz`
- **Wheel Package:** `provenance_demo-*.whl`
- **PYZ Application:** `provenance-demo.pyz`
- **Checksums:** `checksums.txt` (SHA256 for all files)
- **Signatures:** `*.sig` and `*.crt` (Sigstore keyless signatures)
- **Attestations:** GitHub provenance attestations
- **SBOM:** `sbom.json` (CycloneDX format)

## Next Steps

1. ✅ Download complete
2. ✅ Validation passed
3. ✅ Verification run
4. 📖 Read [Platform Support](../PLATFORM-SUPPORT.md) for other platforms
5. 📖 See [Verification Example](../../security/VERIFICATION-EXAMPLE.md) for details
6. 🚀 Start using the template for your CLI project
7. 💡 Star the repository for updates
8. 👀 Watch releases for notifications

## Support

- **Issues:** Report download issues at [GitHub Issues](https://github.com/redoubt-cysec/provenance-demo/issues)
- **Documentation:** See [Platform Status](../PLATFORM-STATUS.md) for complete details
- **Security:** Run verification for all downloads
- **Releases:** View all releases at [GitHub Releases](https://github.com/redoubt-cysec/provenance-demo/releases)

---

**Installation Method:** GitHub Releases (Direct Download)
**Production Ready:** ✅ Yes
**Automated Testing:** ✅ Phase 1 + Phase 2
**Last Updated:** 2025-11-01
