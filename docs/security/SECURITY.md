# Security Policy

## Supported Versions

This is a template repository. Security updates apply to the template itself.

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via:

1. **GitHub Security Advisories** (preferred)
   - Go to the repository Security tab
   - Click "Report a vulnerability"
   - Fill out the form with details

2. **Email** (if GitHub is not available)
   - Contact: [YOUR_SECURITY_EMAIL]
   - Use subject: "SECURITY: [brief description]"
   - Include:
     - Description of the vulnerability
     - Steps to reproduce
     - Potential impact
     - Suggested fix (if any)

### What to expect

- **Initial Response:** Within 48 hours
- **Updates:** Every 72 hours until resolved
- **Fix Timeline:** Critical issues within 7 days, others within 30 days
- **Disclosure:** Coordinated disclosure after fix is available

## Security Features

This template includes:

### Build Security

- ✅ Reproducible builds with SOURCE_DATE_EPOCH
- ✅ Deterministic artifacts (verifiable hashes)
- ✅ Isolated build environment

### Cryptographic Security

- ✅ Keyless signing via Sigstore/cosign
- ✅ Rekor transparency log
- ✅ Fulcio certificate authority
- ✅ GitHub build provenance attestation (SLSA)

### Supply Chain Security

- ✅ CycloneDX SBOM generation
- ✅ OSV vulnerability scanning
- ✅ GitHub Actions pinned to commit SHAs
- ✅ Harden-runner egress control
- ✅ Minimal workflow permissions

### Verification

- ✅ Automated verification scripts
- ✅ From-source reproducibility checks
- ✅ Attestation validation
- ✅ Checksum verification

## Security Testing

This repository includes comprehensive security tests:

```bash
# Run security test suite
uv run pytest tests/ -m "not slow"

# See SECURITY-TESTING.md for details
```

**79 security tests** covering:

- Cryptographic integrity (30 tests)
- Supply chain security (15 tests)
- Runtime security (12 tests)
- Workflow hardening (10 tests)
- Build reproducibility (5 tests)
- SBOM & vulnerabilities (6 tests)

## Security Best Practices

When using this template:

### 1. Configuration

- [ ] Replace all `<PINNED_SHA>` with actual commit SHAs
- [ ] Set up GitHub environment protection for releases
- [ ] Enable branch protection for `main` and `v*` tags
- [ ] Require status checks and reviews
- [ ] Add `TAP_PUSH_TOKEN` and `WINGET_GITHUB_TOKEN` secrets (if using)

### 2. Maintenance

- [ ] Run security tests in CI/CD
- [ ] Enable Dependabot or Renovate for dependency updates
- [ ] Monitor OSV scan results
- [ ] Review Scorecards reports weekly
- [ ] Audit workflow changes carefully

### 3. Development

- [ ] Install pre-commit hooks: `pre-commit install`
- [ ] Run tests before committing: `uv run pytest tests/`
- [ ] Never commit secrets (.env, *.pem,*.key)
- [ ] Use `uv` for reproducible environments

### 4. Releases

- [ ] All tests must pass
- [ ] Tag with semantic versioning (vX.Y.Z)
- [ ] Verify signed artifacts
- [ ] Check SBOM and vulnerability report
- [ ] Review build provenance

## Known Limitations

### Template Placeholders

- Workflows use `<PINNED_SHA>` placeholders
- Replace with actual commit SHAs before production use
- See DEVELOPER_GUIDE.md for instructions

### Build Environment

- Builds on GitHub-hosted runners (Ubuntu latest)
- Runner security depends on GitHub infrastructure
- Use self-hosted runners for additional control

### Verification

- GitHub CLI required for attestation verification
- cosign required for signature verification
- Both must be installed by end users

## Security Checklist

Before your first release:

- [ ] Replace `Borduas-Holdings/redoubt-release-template` throughout the repository
- [ ] Pin all GitHub Actions to commit SHAs
- [ ] Set up branch protection rules
- [ ] Enable GitHub environment protection
- [ ] Configure required secrets (if using Homebrew/Winget)
- [ ] Run full test suite: `uv run pytest tests/ -v`
- [ ] Enable Dependabot/Renovate
- [ ] Set up vulnerability alerts
- [ ] Review and customize SECURITY.md

## Threat Model

### In Scope

- Supply chain attacks (compromised dependencies, actions)
- Build tampering
- Credential theft
- Code injection
- Privilege escalation in workflows
- Man-in-the-middle attacks on artifacts

### Out of Scope

- Attacks on GitHub infrastructure
- Social engineering
- Physical access to developer machines
- Zero-day vulnerabilities in Python/GitHub Actions
- DDoS attacks

## Security Contacts

For security-related questions:

- **Template Issues:** GitHub Issues (non-sensitive)
- **Vulnerabilities:** GitHub Security Advisories (sensitive)
- **General Questions:** Discussions tab

## Acknowledgments

We welcome security researchers to review this template. Responsible disclosure is appreciated.

### Hall of Fame

Contributors who have responsibly disclosed vulnerabilities:

- (None yet - be the first!)

## References

- [Sigstore Documentation](https://docs.sigstore.dev/)
- [SLSA Framework](https://slsa.dev/)
- [OpenSSF Best Practices](https://bestpractices.coreinfrastructure.org/)
- [GitHub Actions Security](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [NIST SSDF](https://csrc.nist.gov/Projects/ssdf)
