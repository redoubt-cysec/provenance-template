# Supply-Chain Security & Verification

This template ships a hardened, reproducible pipeline with **14 comprehensive security checks**.

## Quick Verification (Recommended)

Download all release artifacts and run the built-in verification:

```bash
# Set your release details
TAG=v0.0.1-alpha.40
REPO=redoubt-cysec/provenance-template

# Download all release artifacts
gh release download $TAG --repo $REPO

# Run comprehensive verification (14/14 checks)
GITHUB_REPOSITORY=$REPO python3 provenance-demo.pyz verify
```

This automatically verifies:
- Checksums
- Sigstore signatures
- Rekor transparency log
- GitHub attestations
- SBOM validity
- Vulnerability scans
- SLSA provenance
- Build reproducibility
- And 6 more checks

## Manual Verification Steps

### 1. Verify GitHub Attestations

```bash
gh attestation verify provenance-demo.pyz --repo $REPO
```

### 2. Verify Checksums

```bash
# Download checksum manifest
curl -LO https://github.com/$REPO/releases/download/$TAG/checksums.txt

# Verify checksum
sha256sum -c checksums.txt --ignore-missing
```

### 3. Verify Sigstore Signature

```bash
# Download signature bundle
curl -LO https://github.com/$REPO/releases/download/$TAG/provenance-demo.pyz.sigstore

# Verify signature with cosign
cosign verify-blob \
  --bundle provenance-demo.pyz.sigstore \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  --certificate-identity-regexp "^https://github.com/$REPO/" \
  provenance-demo.pyz
```

### 4. Verify SBOM and Vulnerabilities

```bash
# Download SBOM files
curl -LO https://github.com/$REPO/releases/download/$TAG/sbom.spdx.json
curl -LO https://github.com/$REPO/releases/download/$TAG/sbom.cyclonedx.json

# Download vulnerability scan results
curl -LO https://github.com/$REPO/releases/download/$TAG/osv-scan-results.json
curl -LO https://github.com/$REPO/releases/download/$TAG/osv-scan-report.txt

# Verify no vulnerabilities found
cat osv-scan-report.txt
```

## Release Artifacts

Each release includes:

- `provenance-demo.pyz` - Single-file Python zipapp executable
- `provenance-demo.pyz.sigstore` - Sigstore cosign signature bundle
- `attestation.jsonl` - GitHub attestations (SBOM + SLSA provenance)
- `sbom.spdx.json` - SPDX Software Bill of Materials
- `sbom.cyclonedx.json` - CycloneDX Software Bill of Materials
- `checksums.txt` - SHA256 checksums of all artifacts
- `osv-scan-results.json` - OSV vulnerability scan (JSON format)
- `osv-scan-report.txt` - OSV vulnerability scan (human-readable)
- `build-metadata.json` - Build metadata with SOURCE_DATE_EPOCH
- `provenance-demo.{version}.nupkg` - Chocolatey package for Windows

## Security Properties

1. **Deterministic Builds**: Builds produce byte-for-byte identical artifacts given the same source
2. **Provenance Attestations**: GitHub SLSA provenance linked to specific commit, workflow, and runner
3. **Keyless Signatures**: Checksums signed with cosign using OIDC (no long-lived keys)
4. **SBOM**: Complete dependency graph in CycloneDX format
5. **Vulnerability Scanning**: Pre-release OSV and pip-audit scans
6. **Hardened CI**: Egress firewall, pinned actions, minimal permissions
7. **Rebuilder Workflow**: Independent verification of reproducibility

## Threat Model

This pipeline defends against:

- Compromised build environments (provenance + determinism)
- Dependency confusion (SBOM + scanning)
- Supply chain injection (hardened CI, egress control)
- Key compromise (keyless signatures)
- Artifact tampering (checksums + attestations)

For security issues, see [SECURITY.md](SECURITY.md).
