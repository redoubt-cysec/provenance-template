# Supply-Chain Security & Verification

This template ships a hardened, reproducible pipeline.

## Verify the Release (fast path)

```bash
# Download and verify attestation
TAG=v0.1.0
REPO=redoubt-cysec/provenance-demo
curl -LO https://github.com/$REPO/releases/download/$TAG/client.pyz
gh attestation verify client.pyz --repo $REPO
```

## Verify with Checksums (+ cosign optional)

```bash
curl -LO https://github.com/$REPO/releases/download/$TAG/SHA256SUMS
curl -LO https://github.com/$REPO/releases/download/$TAG/SHA256SUMS.bundle
sha256sum --check SHA256SUMS --ignore-missing
COSIGN_EXPERIMENTAL=1 cosign verify-blob \
  --bundle SHA256SUMS.bundle \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  --certificate-identity "https://github.com/$REPO/.github/workflows/Secure Release@refs/tags/$TAG" \
  SHA256SUMS
```

## Rebuild from Source (reproducible)

```bash
./scripts/verify_build.sh v0.1.0 OWNER REPO client.pyz
./scripts/verify_provenance.sh v0.1.0 OWNER REPO client.pyz
```

## Artifacts

Each release includes:

- `client.pyz` - Single-file Python zipapp executable
- `sbom.cdx.json` - CycloneDX Software Bill of Materials
- `SHA256SUMS` - Checksums of all artifacts
- `SHA256SUMS.bundle` - Sigstore cosign signature bundle
- `vuln-report.json` - Vulnerability scan results from pip-audit

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
