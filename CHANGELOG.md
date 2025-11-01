# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.1-alpha.40] - 2025-11-01

### Achievement: 100% Verification ✓

This release achieves **14/14 (100%)** comprehensive security verification checks.

### Added
- Complete 14-check verification system covering:
  - Checksum verification with release manifest
  - Sigstore signature verification
  - Certificate identity verification
  - Rekor transparency log verification
  - GitHub attestation verification
  - SBOM attestation verification
  - SBOM validation (SPDX + CycloneDX)
  - OSV vulnerability scanning
  - SLSA provenance verification
  - Build environment verification
  - Reproducible build verification (SOURCE_DATE_EPOCH)
  - Artifact metadata verification
  - License compliance checking
  - Dependency pinning verification

- Security features implemented:
  - Checksum generation (checksums.txt) in release workflow
  - BUILD-metadata.json with SOURCE_DATE_EPOCH for reproducibility
  - OSV vulnerability scanning integration
  - SLSA provenance attestation download and verification
  - Sigstore/Cosign keyless signing
  - Rekor transparency log integration

- Documentation updates:
  - Comprehensive VERIFICATION-EXAMPLE.md with all 14 checks explained
  - Updated README.md with actual 14/14 verification output
  - Accurate SUPPLY-CHAIN.md with correct artifact names and commands

### Fixed
- [#55](https://github.com/redoubt-cysec/provenance-template/pull/55) - Rekor bundle file extension (.sigstore vs .sigstore.json)
- [#54](https://github.com/redoubt-cysec/provenance-template/pull/54) - Attestation parsing to handle dsseEnvelope wrapper format
- [#53](https://github.com/redoubt-cysec/provenance-template/pull/53) - Attestation download and Rekor bundle format support
- [#52](https://github.com/redoubt-cysec/provenance-template/pull/52) - GitHub attestation download workflow
- [#51](https://github.com/redoubt-cysec/provenance-template/pull/51) - Three quick wins (checksums, metadata, dependency pinning)

### Changed
- Verification increased from 5/14 (36%) to 14/14 (100%)
- Enhanced attestation parsing to support multiple formats
- Improved error messages and verification output

### Migration Notes
- For full verification, install: `cosign`, `gh`, `osv-scanner`
- Set `GITHUB_REPOSITORY` environment variable when running verify command
- All changes are backward compatible

## Earlier Releases

See [GitHub Releases](https://github.com/redoubt-cysec/provenance-template/releases) for v0.0.1-alpha.35 and earlier.

[Unreleased]: https://github.com/redoubt-cysec/provenance-template/compare/v0.0.1-alpha.40...HEAD
[0.0.1-alpha.40]: https://github.com/redoubt-cysec/provenance-template/releases/tag/v0.0.1-alpha.40
