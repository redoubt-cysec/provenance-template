# Quick Start Guides

**Production-Ready Platforms | Complete Installation & Validation**

This directory contains comprehensive quick start guides for all 7 production-ready platforms. Each guide includes installation instructions, validation scripts, troubleshooting, and best practices.

## Choose Your Platform

### Python Developers

**[PyPI (pip/uv)](PYPI.md)** - Standard Python package installation
- Installation: `pip install provenance-demo` or `uv pip install provenance-demo`
- Best for: Python developers, CI/CD pipelines, standard environments
- Validation: [validate-pypi.sh](../../../scripts/validation/validate-pypi.sh)
- Status: ✅ Production Ready | Phase 1 + Phase 2 Tested

**[pipx](PIPX.md)** - Isolated environment installation
- Installation: `pipx install provenance-demo`
- Best for: CLI tools, avoiding dependency conflicts, user installations
- Validation: [validate-pipx.sh](../../../scripts/validation/validate-pipx.sh)
- Status: ✅ Production Ready | Phase 1 + Phase 2 Tested

**[Direct .pyz Execution](PYZ.md)** - Single-file executable
- Installation: Download `.pyz` file, make executable
- Best for: Air-gapped systems, minimal dependencies, reproducible environments
- Validation: [validate-pyz.sh](../../../scripts/validation/validate-pyz.sh)
- Status: ✅ Production Ready | Phase 1 + Phase 2 Tested

### Package Manager Users

**[Homebrew (macOS/Linux)](HOMEBREW.md)** - Universal package manager
- Installation: `brew tap OWNER/tap && brew install redoubt`
- Best for: macOS users, Linuxbrew users, version management
- Validation: [validate-homebrew.sh](../../../scripts/validation/validate-homebrew.sh)
- Status: ✅ Production Ready | Phase 1 + Phase 2 Tested

**[Snap (Linux)](SNAP.md)** - Universal Linux package
- Installation: `snap install provenance-demo`
- Best for: Ubuntu, strict confinement, auto-updates
- Validation: [validate-snap.sh](../../../scripts/validation/validate-snap.sh)
- Status: ✅ Production Ready | Phase 1 + Phase 2 Tested

### Container Users

**[Docker/OCI](DOCKER.md)** - Container-based deployment
- Installation: `docker pull ghcr.io/OWNER/redoubt:latest`
- Best for: Containerized environments, Kubernetes, CI/CD
- Validation: [validate-docker.sh](../../../scripts/validation/validate-docker.sh)
- Status: ✅ Production Ready | Phase 1 + Phase 2 Tested

### Direct Downloads

**[GitHub Releases](GITHUB-RELEASES.md)** - Direct artifact download
- Installation: Download from GitHub Releases page
- Best for: Manual installation, verification-first approach, offline distribution
- Validation: [validate-github-releases.sh](../../../scripts/validation/validate-github-releases.sh)
- Status: ✅ Production Ready | Phase 1 + Phase 2 Tested

## Platform Comparison

| Platform | Install Time | Dependencies | Auto-Update | Isolation | Verification |
|----------|-------------|--------------|-------------|-----------|--------------|
| **PyPI** | ~10s | Python 3.11+ | Manual | Shared | ✅ Full |
| **pipx** | ~15s | Python 3.11+ | Manual | Isolated | ✅ Full |
| **.pyz** | ~5s | Python 3.11+ | Manual | None | ✅ Full |
| **Homebrew** | ~20s | None | Auto | Isolated | ✅ Full |
| **Snap** | ~30s | None | Auto | Strict | ✅ Full |
| **Docker** | ~1m | Docker | Manual | Complete | ✅ Full |
| **GitHub** | ~5s | Python 3.11+ | Manual | None | ✅ Full |

## Quick Decision Guide

### I want the fastest installation
→ **[.pyz](PYZ.md)** or **[GitHub Releases](GITHUB-RELEASES.md)** (~5 seconds)

### I want automatic updates
→ **[Homebrew](HOMEBREW.md)** or **[Snap](SNAP.md)**

### I want complete isolation
→ **[Docker](DOCKER.md)** (complete) or **[pipx](PIPX.md)** (Python-level)

### I'm on macOS
→ **[Homebrew](HOMEBREW.md)** (recommended) or **[PyPI](PYPI.md)**

### I'm on Ubuntu/Debian
→ **[Snap](SNAP.md)** (recommended) or **[PyPI](PYPI.md)**

### I'm in a CI/CD pipeline
→ **[PyPI](PYPI.md)** or **[Docker](DOCKER.md)**

### I'm air-gapped/offline
→ **[.pyz](PYZ.md)** or **[GitHub Releases](GITHUB-RELEASES.md)**

### I want maximum security verification
→ **[GitHub Releases](GITHUB-RELEASES.md)** (verify-first approach)

## Validation Scripts

All platforms include automated validation scripts in [scripts/validation/](../../../scripts/validation/):

```bash
# Validate specific platform
./scripts/validation/validate-pypi.sh
./scripts/validation/validate-pipx.sh
./scripts/validation/validate-pyz.sh
./scripts/validation/validate-github-releases.sh
./scripts/validation/validate-homebrew.sh
./scripts/validation/validate-snap.sh
./scripts/validation/validate-docker.sh

# Validate all platforms
./scripts/validation/validate-all.sh

# Validate specific platforms only
./scripts/validation/validate-all.sh --platforms=pypi,docker

# Continue on error
./scripts/validation/validate-all.sh --continue-on-error
```

See [validation/README.md](../../../scripts/validation/README.md) for complete documentation.

## What Each Guide Contains

Every quick start guide includes:

1. **Installation** - Step-by-step installation instructions
2. **Verification** - How to verify the installation works
3. **Validation Script** - Automated testing script
4. **Upgrading** - How to upgrade to newer versions
5. **Uninstalling** - How to cleanly remove the package
6. **Troubleshooting** - Common issues and solutions
7. **Best Practices** - Recommended usage patterns
8. **Platform-Specific Notes** - Important platform details
9. **Security Verification** - How to verify supply chain security
10. **Next Steps** - Where to go after installation

## Common Post-Installation Steps

After installing via any method:

```bash
# 1. Verify installation
provenance-demo --version

# 2. Test basic functionality
provenance-demo hello world

# 3. Run comprehensive verification
export GITHUB_REPOSITORY=redoubt-cysec/provenance-template
gh release download v0.1.0 --repo $GITHUB_REPOSITORY
provenance-demo verify

# Expected: ✓ 14/14 checks passed
```

## Platform Status

For detailed status, testing coverage, and production readiness:
- **[Platform Status](../PLATFORM-STATUS.md)** - Complete status table
- **[Platform Support](../PLATFORM-SUPPORT.md)** - Full platform guide

### Summary

- **✅ 7 Production-Ready Platforms** with full testing and documentation
- **✅ 14/14 Verification Checks** pass on all platforms
- **✅ Phase 1 + Phase 2 Testing** complete
- **✅ Automated Validation Scripts** for all platforms

## Troubleshooting

### Installation Issues

**Problem:** Command not found after installation

**Solutions by platform:**
- **PyPI/pipx:** Check PATH includes Python scripts directory
- **Homebrew:** Run `brew doctor` to check installation
- **Snap:** Ensure `/snap/bin` is in PATH
- **Docker:** Use `docker run` instead of direct command

See platform-specific guides for detailed troubleshooting.

### Verification Issues

**Problem:** Verification checks fail

**Solutions:**
1. Ensure all verification tools are installed (cosign, gh, osv-scanner)
2. Check network connectivity
3. Download release artifacts first
4. Set GITHUB_REPOSITORY environment variable

See [Verification Example](../../security/VERIFICATION-EXAMPLE.md) for step-by-step guide.

### Version Mismatch

**Problem:** Wrong version installed

**Solutions:**
- **PyPI:** `pip install --upgrade provenance-demo`
- **pipx:** `pipx upgrade provenance-demo`
- **Homebrew:** `brew upgrade redoubt`
- **Snap:** `snap refresh provenance-demo`
- **Docker:** `docker pull ghcr.io/OWNER/redoubt:latest`

## Security Best Practices

### Always Verify After Installation

```bash
# Method 1: Built-in verification
provenance-demo verify

# Method 2: GitHub CLI
gh attestation verify $(which provenance-demo) --repo redoubt-cysec/provenance-demo

# Method 3: Cosign
cosign verify-blob provenance-demo.pyz --bundle provenance-demo.pyz.sigstore \
  --certificate-identity-regexp=".*" \
  --certificate-oidc-issuer-regexp=".*"
```

### Pin to Specific Versions

```bash
# PyPI
pip install provenance-demo==0.1.0

# Homebrew
brew install redoubt@0.1.0

# Docker
docker pull ghcr.io/OWNER/redoubt:0.1.0
```

### Verify Checksums

All platforms support SHA256 checksum verification:

```bash
# Download checksum file
gh release download v0.1.0 --repo redoubt-cysec/provenance-demo --pattern 'checksums.txt'

# Verify artifact
sha256sum -c checksums.txt
```

## Additional Resources

### Documentation
- [Supply Chain Security](../../security/SUPPLY-CHAIN.md) - Complete security guide
- [Verification Example](../../security/VERIFICATION-EXAMPLE.md) - Step-by-step verification
- [Security Testing](../../security/SECURITY-TESTING.md) - Details on 178 security tests

### Platform Details
- [Platform Status](../PLATFORM-STATUS.md) - Detailed platform status table
- [Platform Support](../PLATFORM-SUPPORT.md) - Complete platform support guide
- [Publishing Guide](../PUBLISHING-GUIDE.md) - How to publish to platforms

### Development
- [Developer Guide](../../contributing/DEVELOPER-GUIDE.md) - Customize the template
- [Contributing](../../contributing/CONTRIBUTING.md) - How to contribute
- [Testing Strategy](../../testing/TESTING-STRATEGY.md) - Testing approach

## Support

- **Issues:** [GitHub Issues](https://github.com/redoubt-cysec/provenance-demo/issues)
- **Security:** See [Security Policy](../../security/SECURITY.md)
- **Questions:** Check platform-specific guides first

## Contributing

To improve these guides:

1. Test installation on your platform
2. Document any issues or improvements
3. Submit PR with updates
4. Add validation test if applicable

See [Contributing Guide](../../contributing/CONTRIBUTING.md) for details.

---

**Quick Start Guides Directory**
**Last Updated:** 2025-11-01
**Platforms Covered:** 7 production-ready platforms
**Total Documentation:** 3,254 lines across 7 guides
**Validation Scripts:** 8 automated scripts (669 lines)
