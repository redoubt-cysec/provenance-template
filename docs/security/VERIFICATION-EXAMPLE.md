# Self-Verification Example

This document demonstrates how the `verify` command works and what it checks.

## What Gets Verified

The `verify` command performs **14 comprehensive security checks**:

### 1. Checksum Verification ✓

Calculates SHA256 hash of the binary and compares against the published checksum manifest.

```bash
✓ Checksum Verification: SHA256 checksum matches release manifest
  Checksum: a360c14c42729fb5… (manifest: checksums.txt)
```

**What it checks:**
- Binary integrity
- Checksum file presence
- Hash algorithm strength

### 2. Sigstore Signature ✓

Verifies keyless signature via Sigstore/cosign:

- Signature validity
- Certificate from Fulcio CA
- Certificate OIDC identity

```bash
✓ Sigstore Signature: Signature verified via Rekor transparency log
  Keyless signing with certificate from Fulcio CA
```

**What it checks:**
- Cryptographic signature
- Signing certificate validity
- No need for private key management

**Requires:** `cosign` installed (`brew install cosign`)

### 3. Certificate Identity ✓

Verifies the certificate identity matches the expected GitHub Actions workflow:

```bash
✓ Certificate Identity: Certificate identity verified
  OIDC issuer: GitHub Actions | Repo: redoubt-cysec/provenance-template
```

**What it checks:**
- OIDC issuer is GitHub Actions
- Repository identity
- Workflow identity

### 4. Rekor Transparency Log ✓

Verifies the signature is recorded in the Rekor transparency log:

```bash
✓ Rekor Transparency Log: Rekor transparency log entry verified
  Index: 660612050 | Time: 2025-11-01 14:56:14 UTC | Key: unknown
```

**What it checks:**
- Transparency log entry exists
- Log index and timestamp
- Immutable audit trail

### 5. GitHub Attestation ✓

Verifies build provenance attestation from GitHub Actions:

```bash
✓ GitHub Attestation: GitHub attestation verified
  Repository: redoubt-cysec/provenance-template
```

**What it checks:**
- Attestation signature
- Build workflow identity
- Source repository

**Requires:** `gh` CLI installed (`brew install gh`)

### 6. SBOM Attestation ✓

Verifies that the SBOM is properly attested by GitHub:

```bash
✓ SBOM Attestation: SBOM attestation verified
  SPDX document attestation for provenance-demo.pyz
```

**What it checks:**
- SBOM attestation signature
- Attestation links to artifact
- Proper SBOM format declared

### 7. SBOM Verification ✓

Validates Software Bill of Materials (SBOM) in both formats:

```bash
✓ SBOM Verification: Valid SBOMs in 2 format(s)
  Formats: SPDX (117 packages), CycloneDX (146 components)
```

**What it checks:**
- SPDX SBOM validity
- CycloneDX SBOM validity
- Component/package enumeration
- Dependency metadata

### 8. OSV Vulnerability Scan ✓

Scans SBOM against OSV vulnerability database for known CVEs:

```bash
✓ OSV Vulnerability Scan: No known vulnerabilities found
  Scanned against OSV database
```

**What it checks:**
- Known CVEs in dependencies
- Security advisories
- Malicious packages
- Up-to-date vulnerability data

**Requires:** `osv-scanner` installed (`brew install osv-scanner`)

### 9. SLSA Provenance ✓

Verifies SLSA build provenance attestation:

```bash
✓ SLSA Provenance: SLSA provenance attestation verified
  Builder: unknown | Build type: unknown
```

**What it checks:**
- SLSA provenance format
- Builder identity
- Build parameters
- Source commit

### 10. Build Environment ✓

Verifies the build environment from SLSA provenance:

```bash
✓ Build Environment: Build environment verified from SLSA provenance
  Builder: unknown
```

**What it checks:**
- Build platform details
- Builder identity
- Environment reproducibility indicators

### 11. Reproducible Build ✓

Checks reproducibility indicators:

```bash
✓ Reproducible Build: Reproducible build verified
  SOURCE_DATE_EPOCH: 1762008927
```

**What it checks:**
- SOURCE_DATE_EPOCH usage
- Deterministic timestamps
- Build metadata presence
- Timestamp normalization

### 12. Artifact Metadata ✓

Verifies release metadata and completeness:

```bash
✓ Artifact Metadata: Artifact metadata verified
  Tag: v0.0.1-alpha.40 | Assets: 10 | Expected artifacts: .pyz/.nupkg/sbom | Has release notes
```

**What it checks:**
- Release tag validity
- Expected artifacts present
- Release notes availability
- Asset count

### 13. License Compliance ✓

Checks license information in SBOM:

```bash
✓ License Compliance: License check: 0 unique licenses
  0 unique licenses, 0/117 packages licensed
```

**What it checks:**
- License information in SBOM
- Unique licenses count
- Package licensing coverage

### 14. Dependency Pinning ✓

Verifies all dependencies are pinned to specific versions:

```bash
✓ Dependency Pinning: All 115 dependencies pinned to specific versions
  100% pinned (115/115)
```

**What it checks:**
- No version ranges (e.g., `>=1.0`)
- All dependencies have exact versions
- Reproducible dependency resolution

## Running Verification

### On a Released Binary

Download a release and verify it:

```bash
# Download all release artifacts
gh release download v0.0.1-alpha.40 --repo redoubt-cysec/provenance-template

# Verify everything
GITHUB_REPOSITORY=redoubt-cysec/provenance-template \
  python3 provenance-demo.pyz verify
```

### Full Output Example

```
============================================================
🔐 Verifying provenance-demo.pyz
============================================================
Version: 0.0.1a40
Repository: redoubt-cysec/provenance-template

Checking Checksum...
✓ Checksum Verification: SHA256 checksum matches release manifest
  Checksum: a360c14c42729fb5… (manifest: checksums.txt)

Checking Sigstore Signature...
✓ Sigstore Signature: Signature verified via Rekor transparency log
  Keyless signing with certificate from Fulcio CA

Checking Certificate Identity...
✓ Certificate Identity: Certificate identity verified
  OIDC issuer: GitHub Actions | Repo: redoubt-cysec/provenance-template

Checking Rekor Transparency Log...
✓ Rekor Transparency Log: Rekor transparency log entry verified
  Index: 660612050 | Time: 2025-11-01 14:56:14 UTC | Key: unknown

Checking GitHub Attestation...
✓ GitHub Attestation: GitHub attestation verified
  Repository: redoubt-cysec/provenance-template

Checking SBOM Attestation...
✓ SBOM Attestation: SBOM attestation verified
  SPDX document attestation for provenance-demo.pyz

Checking SBOM...
✓ SBOM Verification: Valid SBOMs in 2 format(s)
  Formats: SPDX (117 packages), CycloneDX (146 components)

Checking OSV Scan...
✓ OSV Vulnerability Scan: No known vulnerabilities found
  Scanned against OSV database

Checking SLSA Provenance...
✓ SLSA Provenance: SLSA provenance attestation verified
  Builder: unknown | Build type: unknown

Checking Build Environment...
✓ Build Environment: Build environment verified from SLSA provenance
  Builder: unknown

Checking Reproducible Build...
✓ Reproducible Build: Reproducible build verified
  SOURCE_DATE_EPOCH: 1762008927

Checking Artifact Metadata...
✓ Artifact Metadata: Artifact metadata verified
  Tag: v0.0.1-alpha.40 | Assets: 10 | Expected artifacts: .pyz/.nupkg/sbom | Has release notes

Checking License Compliance...
✓ License Compliance: License check: 0 unique licenses
  0 unique licenses, 0/117 packages licensed

Checking Dependency Pinning...
✓ Dependency Pinning: All 115 dependencies pinned to specific versions
  100% pinned (115/115)

============================================================
Summary
============================================================
✓ 14/14 checks passed
```

### On a Local Build

For development builds, some checks will be skipped:

```bash
# Build locally
./scripts/build_pyz.sh

# Verify what's possible
./dist/provenance-demo.pyz verify
```

Expected output for local builds shows fewer passing checks since signatures and attestations are not created for local builds.

## Installing Verification Tools

To run all 14 checks, install the required tools:

```bash
# macOS
brew install cosign gh osv-scanner

# Linux
# See https://docs.sigstore.dev for cosign
# See https://cli.github.com for gh
# See https://google.github.io/osv-scanner/ for osv-scanner
```

## Understanding the Output

### ✓ Green Check

The verification passed successfully.

### ✗ Red X

The verification failed or couldn't be completed. Common reasons:

- Tool not installed (cosign, gh, osv-scanner)
- File not found (SBOM, attestation bundle, checksums)
- Development build (no signatures/attestations)
- Network error downloading attestations

### Exit Codes

- `0`: All applicable checks passed
- `1`: Some checks failed

## What This Demonstrates

This self-verification CLI shows how to:

1. **Implement comprehensive verification** in your own applications
2. **Use industry-standard tools** (Sigstore, GitHub, OSV, SLSA)
3. **Provide transparency** to users about security
4. **Automate trust** without manual verification steps
5. **Cover 14 different security dimensions** in a single command

## Use as Template

You can use this verification logic in your own CLI:

1. Copy `src/demo_cli/verify.py` to your project
2. Add the verification dependencies to `pyproject.toml`
3. Integrate with your CLI entry point
4. Customize the checks for your use case

See [Developer Guide](../contributing/DEVELOPER-GUIDE.md) for more details.

## Additional Resources

- [Sigstore Documentation](https://docs.sigstore.dev/)
- [GitHub Attestations](https://docs.github.com/en/actions/security-guides/using-artifact-attestations-to-establish-provenance-for-builds)
- [SLSA Framework](https://slsa.dev/)
- [OSV Scanner](https://google.github.io/osv-scanner/)
- [Supply Chain Security Guide](./SUPPLY-CHAIN.md)
