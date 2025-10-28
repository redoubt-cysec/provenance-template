# Security Policy

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

### Preferred Method: Private Vulnerability Reporting

We use GitHub's private vulnerability reporting feature. To report a security vulnerability:

1. Go to the [Security tab](../../security)
2. Click "Report a vulnerability"
3. Fill out the advisory form with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Affected versions
   - Suggested fix (if any)

### Alternative: Email

If you cannot use GitHub's private reporting:

- **Email:** security@[YOUR-DOMAIN].com
- **Subject:** `SECURITY: [brief description]`
- **Include:** Same details as above

### Response Timeline

- **Initial Response:** Within 48 hours
- **Status Updates:** Every 72 hours until resolved
- **Fix Timeline:**
  - Critical vulnerabilities: Within 7 days
  - High severity: Within 14 days
  - Other issues: Within 30 days
- **Disclosure:** Coordinated disclosure after fix is available and users have time to update

## Supported Versions

This is a template repository. Security updates apply to the template itself.

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| < 1.0   | :x:                |

## Security Features

This template includes enterprise-grade supply chain security:

- **Cryptographic Signing:** Sigstore/cosign keyless signing with Rekor transparency log
- **Build Attestations:** GitHub provenance attestations with SLSA compliance
- **SBOM:** CycloneDX Software Bill of Materials with OSV vulnerability scanning
- **Reproducible Builds:** Deterministic builds with hash verification
- **Hardened CI/CD:** Egress firewall, pinned GitHub Actions, minimal permissions
- **25+ Security Tests:** Automated verification of cryptographic integrity and security controls

## Documentation

For complete security documentation, see:

- [Complete Security Policy](docs/security/SECURITY.md) - Detailed security information
- [Supply Chain Security](docs/security/SUPPLY-CHAIN.md) - Verify releases and attestations
- [Security Testing](docs/security/SECURITY-TESTING.md) - Details on security test suite
- [Security Checklist](docs/security/COMPLETE-SECURITY-CHECKLIST.md) - Pre-release validation

## Security Contacts

- **Vulnerabilities:** Use private vulnerability reporting (preferred) or email
- **Template Issues:** [GitHub Issues](../../issues) (for non-sensitive topics only)
- **General Questions:** [GitHub Discussions](../../discussions)

## Acknowledgments

We welcome security researchers to review this template. Responsible disclosure is appreciated.

### Hall of Fame

Contributors who have responsibly disclosed vulnerabilities:

- (None yet - be the first!)

---

**For projects using this template:** Customize this file with your own contact information and security processes.
