# Self-Verification Example

This document demonstrates how the `redoubt verify` command works and what it checks.

## What Gets Verified

The `verify` command performs **7 comprehensive security checks**:

### 1. Checksum Verification ✓

Calculates SHA256 hash of the binary and compares against published checksums.

```bash
$ ./provenance-demo.pyz verify
✓ Checksum Verification: SHA256 checksum matches
  Checksum: 76c642b637244d57...
```

### 2. Sigstore Signature ✓

Verifies keyless signature via cosign, checking:

- Signature validity
- Rekor transparency log entry
- Fulcio CA certificate

```bash
✓ Sigstore Signature: Signature verified via Rekor transparency log
  Keyless signing with certificate from Fulcio CA
```

**Requires:** `cosign` installed (`brew install cosign`)

### 3. GitHub Attestation ✓

Verifies build provenance attestation from GitHub Actions:

- Attestation signature
- Build workflow identity
- Source repository

```bash
✓ GitHub Attestation: GitHub attestation verified
  Repository: redoubt-cysec/provenance-demo
```

**Requires:** `gh` CLI installed (`brew install gh`)

### 4. SBOM Verification ✓

Validates Software Bill of Materials (SBOM):

- CycloneDX format validation
- Component enumeration
- Dependency metadata

```bash
✓ SBOM Verification: Valid CycloneDX SBOM with 42 components
  Spec version: 1.5
```

### 5. OSV Vulnerability Scan ✓

Scans SBOM against OSV vulnerability database:

- Known CVEs
- Security advisories
- Malicious packages

```bash
✓ OSV Vulnerability Scan: No known vulnerabilities found
  Scanned against OSV database
```

**Requires:** `osv-scanner` installed (`brew install osv-scanner`)

### 6. SLSA Provenance ✓

Verifies SLSA build provenance:

- Builder identity
- Build parameters
- Source commit

```bash
✓ SLSA Provenance: SLSA provenance attestation found
  Builder: https://github.com/actions/runner/...
```

### 7. Reproducible Build ✓

Checks reproducibility indicators:

- SOURCE_DATE_EPOCH usage
- Deterministic timestamps
- Build environment normalization

```bash
✓ Reproducible Build: Build uses SOURCE_DATE_EPOCH
  Timestamps normalized for reproducibility
```

## Running Verification

### On a Released Binary

Download a release and verify it:

```bash
# Download from GitHub releases
curl -L -o provenance-demo.pyz https://github.com/redoubt-cysec/provenance-demo/releases/download/v0.1.0/provenance-demo.pyz

# Make executable
chmod +x provenance-demo.pyz

# Verify everything
./provenance-demo.pyz verify
```

### On a Local Build

For development builds, some checks will be skipped:

```bash
# Build locally
./scripts/build_pyz.sh

# Verify what's possible
./dist/provenance-demo.pyz verify
```

Expected output for local builds:

```
🔐 Verifying provenance-demo.pyz
Version: 0.1.0
Repository: redoubt-cysec/provenance-demo

✓ Checksum Verification: Checksum calculated
✗ Sigstore Signature: No signature bundle found (expected for dev builds)
✗ GitHub Attestation: Not available for local builds
✗ SBOM Verification: SBOM file not found
✗ OSV Vulnerability Scan: SBOM not found for scanning
✗ SLSA Provenance: Attestation bundle not found
✓ Reproducible Build: Build metadata present

Summary
2/7 checks passed

⚠ Some verifications failed or are skipped
This may be expected if:
  • You're running a development build (not a release)
  • Security tools (cosign, gh, osv-scanner) are not installed
  • Attestation files are not present locally
```

## Verifying Specific Files

You can verify any `.pyz` file:

```bash
./provenance-demo.pyz verify --file /path/to/other.pyz
```

## Installing Verification Tools

To run all checks, install the required tools:

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
- File not found (SBOM, attestation bundle)
- Development build (no signatures/attestations)

### Exit Codes

- `0`: All checks passed
- `1`: Some checks failed

## What This Demonstrates

This self-verification CLI shows how to:

1. **Implement verification** in your own applications
2. **Use industry-standard tools** (Sigstore, GitHub, OSV)
3. **Provide transparency** to users about security
4. **Automate trust** without manual verification steps

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
