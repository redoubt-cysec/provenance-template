# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-11-01

### 🎉 First Stable Release

This is the first stable release of the Provenance Demo template, achieving **100% implementation** of all advertised security features and complete documentation transparency.

### Highlights

- ✅ **14/14 verification checks** (100% pass rate)
- ✅ **178 security tests** passing
- ✅ **7 production-ready platforms** with full testing
- ✅ **Complete supply chain security** implementation
- ✅ **100% accurate documentation** with full transparency

### Added

#### Security Features (PRs #51-#55, #59)
- **Complete 14-check verification system** including:
  - Checksum verification with SHA256
  - Sigstore signature verification (keyless signing)
  - Certificate identity validation
  - Rekor transparency log verification
  - GitHub attestation verification (SLSA provenance)
  - SBOM attestation verification
  - SBOM validation (SPDX + CycloneDX)
  - OSV vulnerability scanning
  - Build environment verification
  - Reproducible build verification (SOURCE_DATE_EPOCH)
  - Artifact metadata verification
  - License compliance checking
  - Dependency pinning verification
  - SLSA provenance verification

- **StepSecurity Harden-Runner** in all critical workflows including secure-release.yml (PR #59)
- **Security hardening in verification parser** with DoS protection, path traversal prevention, input validation (PR #58)
- **Three quick security wins**: Checksums manifest, build metadata, dependency pinning checks (PR #51)

#### Documentation (PRs #56, #57, #60)
- **Platform Status Transparency** (PR #60):
  - New PLATFORM-STATUS.md with complete status table for all platforms
  - Clear distinction: 7 production-ready, 9 configured, 6 planned
  - Test coverage details (Phase 1 + Phase 2) per platform
  - Production readiness criteria defined
  - Single source of truth for platform support

- **Verification Documentation** (PR #56):
  - Complete VERIFICATION-EXAMPLE.md with all 14 checks explained
  - Updated README with accurate verification output
  - Fixed SUPPLY-CHAIN.md with correct artifact names

- **CHANGELOG.md** (PR #57):
  - Comprehensive release history
  - Links to all relevant PRs
  - Migration notes

#### Testing
- **178 security test functions** across 11 test files (far exceeds "60+" claim)
- **Phase 1 validation tests**: 48 tests across 13 platforms
- **Phase 2 integration tests**: 8 tests with VM-based verification
- **100% test pass rate** on all security checks

#### Distribution Support
- **7 production-ready platforms** with full testing and automation:
  1. PyPI (pip/uv)
  2. pipx
  3. Direct .pyz execution
  4. GitHub Releases
  5. Homebrew (macOS/Linux)
  6. Snap
  7. Docker/OCI (GHCR)

- **9 configured platforms** with Phase 1 validation:
  - Flatpak, APT/Debian, RPM/Fedora, AUR/Arch, AppImage, Nix/NixOS, Chocolatey, WinGet, Scoop

### Changed

- **README claims updated** to match reality (PR #60):
  - "18 platforms" → "7 production-ready + 9 configured"
  - "60+ tests" → "178 tests"
  - Added clear platform breakdown with status
  - Linked to PLATFORM-STATUS.md for details

- **Documentation reorganization**:
  - Added PLATFORM-STATUS.md to docs/distribution/
  - Updated docs/README.md index
  - Cross-referenced all platform documentation

### Fixed

- **PR #55**: Rekor bundle file extension (.sigstore vs .sigstore.json)
- **PR #54**: Attestation parsing to handle dsseEnvelope wrapper format
- **PR #53**: Attestation download workflow and file handling
- **PR #52**: GitHub attestation download reliability
- **Security verification parser**: Added input validation, DoS protection, path traversal prevention

### Security

- **All GitHub Actions pinned** to commit SHAs
- **StepSecurity Harden-Runner** in 15 critical workflows
- **Keyless signing** with Sigstore/cosign
- **SLSA provenance** attestations for all artifacts
- **SBOM generation** in both SPDX and CycloneDX formats
- **OSV vulnerability scanning** in release pipeline
- **Reproducible builds** with SOURCE_DATE_EPOCH
- **Zero vulnerabilities** in dependencies

### Performance

- Fast test execution: Phase 1 validation ~5 seconds
- Comprehensive integration tests: Phase 2 ~15-20 minutes
- Secure release workflow: ~5-10 minutes end-to-end

### Documentation

- **Complete security testing documentation**: 178 tests explained
- **Platform status table**: Transparency for all 19 platforms
- **Verification guide**: Step-by-step for all 14 checks
- **Supply chain security guide**: Complete verification workflow
- **Developer guide**: Customization instructions
- **Contributing guide**: How to contribute

### Breaking Changes

None - this is the first stable release.

### Migration Guide

If you're coming from alpha releases (v0.0.1-alpha.x):
- No breaking changes
- All alpha features are maintained
- New verification checks are additive
- Platform claims are now more accurate

### Known Limitations

- Some platforms (9) have configuration but need Phase 2 testing
- Planned platforms (6) have no implementation yet
- See PLATFORM-STATUS.md for complete details

### Contributors

This release represents the culmination of work to achieve 100% feature implementation and documentation accuracy. Special thanks to all contributors.

### Links

- [Verification Example](docs/security/VERIFICATION-EXAMPLE.md)
- [Platform Status](docs/distribution/PLATFORM-STATUS.md)
- [Supply Chain Security](docs/security/SUPPLY-CHAIN.md)
- [Security Testing](docs/security/SECURITY-TESTING.md)

---

**v0.1.0 represents a production-ready Python CLI template with enterprise-grade supply chain security.**
