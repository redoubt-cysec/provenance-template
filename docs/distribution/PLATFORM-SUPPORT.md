# Platform Support Guide

**Last Updated:** 2025-10-25 (Added AppImage, AUR, Nix, Flatpak testing coverage)

Redoubt Release Demo can be installed on multiple platforms through various package managers and distribution methods.

## 🆕 Newly Tested Platforms (2025-10-25)

- **Flatpak**: Phase 1 ✅ / Phase 2 🚧 (Flathub Beta in progress)
- **AppImage**: Phase 1 ✅ / Phase 2 ✅ (Ubuntu/Debian/Fedora VMs)
- **AUR (Arch Linux)**: Phase 1 ✅ / Phase 2 ✅ (Arch VM)
- **Nix**: Phase 1 ✅ / Phase 2 🚧 (Cachix planned for Phase 2)

## 🔐 Signature Policy

- **APT**: Repository metadata signed (`InRelease`, `Release.gpg`) — **required for production**
- **RPM**: Per-package signing with `rpm --addsign` — **required for production**
- **Windows**: SHA256 verification (code signing deferred to Phase 3)
- **Other platforms**: SHA256 checksums provided for all artifacts

## 📦 Supported Platforms

### Linux

#### **Homebrew (Linuxbrew)**

```bash
brew tap OWNER/tap
brew install redoubt
redoubt --version
```

#### **Snap Store**

```bash
snap install redoubt-release-template
redoubt --version
```

#### **APT (Debian/Ubuntu)**

```bash
# Add repository (after publishing)
echo "deb [trusted=yes] https://OWNER.github.io/apt-repo /" | sudo tee /etc/apt/sources.list.d/redoubt.list
sudo apt update
sudo apt install redoubt-release-template
redoubt --version
```

#### **RPM (Fedora/RHEL/openSUSE)**

```bash
# Download and install RPM
curl -L -o redoubt.rpm https://github.com/Borduas-Holdings/redoubt-release-template/releases/download/v0.1.0/redoubt-0.1.0-1.rpm
sudo rpm -i redoubt.rpm
redoubt --version

# Or build from spec file
rpmbuild -ba packaging/rpm/redoubt.spec
```

#### **AUR (Arch Linux)**

```bash
# Using yay
yay -S redoubt-release-template

# Or manually
git clone https://aur.archlinux.org/redoubt-release-template.git
cd redoubt-release-template
makepkg -si
```

#### **Flatpak**

```bash
flatpak install flathub com.OWNER.Redoubt
flatpak run com.OWNER.Redoubt hello world
```

#### **AppImage**

```bash
curl -L -o redoubt-0.1.0-x86_64.AppImage \
  https://github.com/Borduas-Holdings/redoubt-release-template/releases/download/v0.1.0/redoubt-0.1.0-x86_64.AppImage
chmod +x redoubt-0.1.0-x86_64.AppImage
./redoubt-0.1.0-x86_64.AppImage --version
```

#### **Nix/NixOS**

```bash
# Using flakes
nix run github:Borduas-Holdings/redoubt-release-template

# Or add to your configuration.nix
environment.systemPackages = [
  (pkgs.callPackage (fetchTarball "https://github.com/Borduas-Holdings/redoubt-release-template/archive/main.tar.gz") {})
];
```

#### **Direct .pyz Download**

```bash
curl -L -o redoubt-release-template.pyz https://github.com/Borduas-Holdings/redoubt-release-template/releases/download/v0.1.0/redoubt-release-template.pyz
chmod +x redoubt-release-template.pyz
./redoubt-release-template.pyz --version
```

#### **pip/pipx (Universal)**

```bash
# Via pip
pip install redoubt-release-template
redoubt --version

# Via pipx (isolated)
pipx install redoubt-release-template
redoubt --version
```

### macOS

#### **Homebrew**

```bash
brew tap OWNER/tap
brew install redoubt
redoubt --version
```

#### **Direct .pyz Download**

```bash
curl -L -o redoubt-release-template.pyz https://github.com/Borduas-Holdings/redoubt-release-template/releases/download/v0.1.0/redoubt-release-template.pyz
chmod +x redoubt-release-template.pyz
./redoubt-release-template.pyz --version
```

#### **pip/pipx**

```bash
pip install redoubt-release-template
# or
pipx install redoubt-release-template
```

### Windows

#### **Scoop**

```powershell
# Add bucket (after publishing)
scoop bucket add OWNER https://github.com/OWNER/scoop-bucket
scoop install redoubt
redoubt --version
```

#### **WinGet**

```powershell
winget install OWNER.Redoubt
redoubt --version
```

#### **Chocolatey**

```powershell
choco install redoubt
redoubt --version
```

#### **pip/pipx**

```powershell
pip install redoubt-release-template
# or
pipx install redoubt-release-template
```

#### **Direct Download**

```powershell
Invoke-WebRequest -Uri "https://github.com/Borduas-Holdings/redoubt-release-template/releases/download/v0.1.0/redoubt-release-template.pyz" -OutFile "redoubt-release-template.pyz"
python redoubt-release-template.pyz --version
```

### Docker / OCI Containers

#### **Docker Hub**

```bash
docker pull OWNER/redoubt:latest
docker run OWNER/redoubt hello world
docker run OWNER/redoubt verify
```

#### **GitHub Container Registry**

```bash
docker pull ghcr.io/OWNER/redoubt:latest
docker run ghcr.io/OWNER/redoubt hello world
docker run ghcr.io/OWNER/redoubt verify
```

#### **Build Locally**

```bash
docker build -t redoubt .
docker run redoubt --version
```

## 🎯 Installation Verification

After installing via any method, verify the installation:

```bash
# Check version
redoubt --version

# Test basic functionality
redoubt hello world

# Verify all attestations
redoubt verify
```

## 🔐 Security Verification

For maximum security, verify the binary after installation:

### Using gh CLI

```bash
gh attestation verify $(which redoubt) --repo Borduas-Holdings/redoubt-release-template
```

### Using cosign

```bash
# Download signature bundle
curl -L -o redoubt-release-template.pyz.sigstore \
  https://github.com/Borduas-Holdings/redoubt-release-template/releases/download/v0.1.0/redoubt-release-template.pyz.sigstore

# Verify signature
cosign verify-blob redoubt-release-template.pyz \
  --bundle redoubt-release-template.pyz.sigstore \
  --certificate-identity-regexp=".*" \
  --certificate-oidc-issuer-regexp=".*"
```

### Using built-in verification

```bash
redoubt verify
```

This runs 7 comprehensive security checks:

- ✅ Checksum verification
- ✅ Sigstore signature verification
- ✅ GitHub attestation verification
- ✅ SBOM validation
- ✅ OSV vulnerability scan
- ✅ SLSA provenance verification
- ✅ Reproducible build validation

## 📊 Platform Support Matrix

| Platform | Method | Status | VM Tested | Attestation Support |
|----------|--------|--------|-----------|---------------------|
| **Linux** |
| Ubuntu/Debian | APT (.deb) | ✅ Ready | ⏳ Pending | ✅ Yes |
| Fedora/RHEL | RPM (.rpm) | ✅ Ready | ⏳ Pending | ✅ Yes |
| Arch Linux | AUR | ✅ Ready | ⏳ Pending | ✅ Yes |
| Universal Linux | Snap | ✅ Tested | ✅ Yes | ✅ Yes |
| Universal Linux | Flatpak | ✅ Ready | ⏳ Pending | ✅ Yes |
| Universal Linux | AppImage | ✅ Ready | ⏳ Pending | ✅ Yes |
| Universal Linux | Homebrew | ✅ Tested | ✅ Yes | ✅ Yes |
| Universal Linux | Nix/NixOS | ✅ Ready | ⏳ Pending | ✅ Yes |
| Universal Linux | pip/pipx | ✅ Tested | ✅ Yes | ✅ Yes |
| Universal Linux | Direct .pyz | ✅ Tested | ✅ Yes | ✅ Yes |
| All distros | Docker | ✅ Tested | ✅ Yes | ✅ Yes |
| **macOS** |
| macOS | Homebrew | ✅ Tested | ✅ Yes | ✅ Yes |
| macOS | Nix | ✅ Ready | ⏳ Pending | ✅ Yes |
| macOS | pip/pipx | ✅ Tested | ✅ Yes | ✅ Yes |
| macOS | Direct .pyz | ✅ Tested | ✅ Yes | ✅ Yes |
| macOS | Docker | ✅ Tested | ✅ Yes | ✅ Yes |
| **Windows** |
| Windows | Scoop | ✅ Ready | ⏳ Pending | ✅ Yes |
| Windows | WinGet | ✅ Ready | ⏳ Pending | ✅ Yes |
| Windows | Chocolatey | ✅ Ready | ⏳ Pending | ✅ Yes |
| Windows | pip/pipx | ✅ Tested | ⏳ Pending | ✅ Yes |
| Windows | Docker | ✅ Tested | ✅ Yes | ✅ Yes |
| **Containers** |
| All platforms | Docker/OCI | ✅ Tested | ✅ Yes | ✅ Yes |
| **CI/CD** |
| GitHub Actions | Action | ✅ Ready | N/A | ✅ Yes |

## 🚀 Publishing Guide

### For Template Users

When you use this template and want to publish to these platforms:

#### 1. **PyPI** (pip install)

```bash
# Build and upload
uv build
twine upload dist/*
```

#### 2. **Homebrew Tap**

```bash
# Update formula with release SHA256
sha256sum dist/redoubt-release-template.pyz
# Edit packaging/homebrew-tap/Formula/redoubt.rb
# Push to OWNER/homebrew-tap repository
```

#### 3. **Snap Store**

```bash
# Build snap
snapcraft
# Upload to store
snapcraft upload redoubt-release-template_0.1.0_all.snap --release=stable
```

#### 4. **Scoop Bucket**

```bash
# Create bucket repository: OWNER/scoop-bucket
# Add redoubt.json from packaging/scoop/ to bucket
# Update SHA256 hash
```

#### 5. **WinGet**

```bash
# Fork microsoft/winget-pkgs
# Add packaging/winget/manifests/OWNER.redoubt.yaml to manifests/
# Create PR to microsoft/winget-pkgs
```

#### 6. **Docker**

```bash
# Build and push
docker build -t OWNER/redoubt:0.1.0 .
docker tag OWNER/redoubt:0.1.0 OWNER/redoubt:latest
docker push OWNER/redoubt:0.1.0
docker push OWNER/redoubt:latest
```

#### 7. **APT Repository**

```bash
# Build .deb package
dpkg-buildpackage -us -uc
# Set up APT repository (using GitHub Pages or dedicated server)
# Upload .deb to repository
```

## 📝 Platform-Specific Notes

### Snap Confinement

The Snap package uses `strict` confinement for security. It has access to:

- `home` - Read/write to user's home directory
- `network` - Network access for verification commands

### Docker Security

The Docker image:

- Runs as non-root user (UID 1000)
- Contains only the minimal Python runtime + binary
- Uses multi-stage build for small image size
- Includes OCI labels for metadata

### Windows Python Requirement

Windows users need Python 3.10+ installed:

- Scoop: `scoop install python`
- WinGet: `winget install Python.Python.3.10`
- Official: <https://python.org/downloads>

### APT Package Dependencies

The .deb package automatically installs Python 3.10+ as a dependency.

## 🧪 Testing Installations

We use Multipass VMs to test all installation methods:

```bash
# Run integration tests
pytest tests/test_distribution_integration.py -v -m integration
```

This tests:

- ✅ Homebrew installation on Ubuntu VM
- ✅ Snap installation on Ubuntu VM
- ✅ pip/wheel installation on Ubuntu VM
- ✅ pipx installation on Ubuntu VM
- ✅ Direct .pyz execution on Ubuntu VM
- ✅ Cross-Python version compatibility (3.10+)

## 🆘 Troubleshooting

### Python Not Found

Ensure Python 3.10+ is installed:

```bash
python3 --version  # Should show 3.10 or higher
```

### Permission Denied

Make the .pyz executable:

```bash
chmod +x redoubt-release-template.pyz
```

### Verification Fails

Install verification tools:

```bash
# macOS
brew install cosign gh osv-scanner

# Ubuntu/Debian
# See installation guides for each tool
```

### Docker Container Network

If verification fails in Docker, ensure network access:

```bash
docker run --network host OWNER/redoubt verify
```

## 📚 Additional Resources

- [Supply Chain Security Guide](../security/SUPPLY-CHAIN.md)
- [Verification Example](../security/VERIFICATION-EXAMPLE.md)
- [Developer Guide](../contributing/DEVELOPER-GUIDE.md)
- [Integration Testing](../testing/INTEGRATION-TESTING.md)

## 🤝 Contributing

To add support for additional platforms:

1. Create configuration files in appropriate directory
2. Add integration tests in `tests/test_distribution_integration.py`
3. Update this documentation
4. Test with Multipass VMs or Docker
5. Submit PR with platform support

See [CONTRIBUTING.md](../contributing/CONTRIBUTING.md) for details.
