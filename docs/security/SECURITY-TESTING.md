# Security Testing Documentation

This repository includes a comprehensive security test suite that validates all security features are properly configured and functional.

## Test Suite Overview

**Total Tests: 100+** (67 fast unit, 6 slow build, 6 runtime, 24+ integration)

- **Unit Test Execution:** ~0.33 seconds (fast tests only)
- **Integration Test Execution:** ~15-20 minutes (across all platforms)
- **Coverage:** Cryptographic integrity, supply chain security, runtime security, workflow hardening, cross-platform installation

## Test Categories

### 5. Integration Tests (`tests/test_distribution_integration.py`) - 24+ tests

Cross-platform installation and execution validation:

- ✅ Homebrew tap installation (macOS/Linux)
- ✅ Snap installation (Ubuntu)
- ✅ pip/PyPI installation (all platforms)
- ✅ pipx installation
- ✅ Direct .pyz execution (Ubuntu, Debian, Fedora, Alpine, macOS, Windows)
- ✅ Python version compatibility (3.11, 3.12+)
- ✅ End-to-end attestation verification

See [INTEGRATION-TESTING.md](INTEGRATION-TESTING.md) for complete documentation.

---

### 1. CLI Functionality Tests (`tests/test_cli.py`) - 12 tests

Basic CLI functionality and argument parsing:

- ✅ Main function callable and returns correct exit codes
- ✅ Version flag and semantic versioning validation
- ✅ Greeting behavior with various inputs
- ✅ Argument parsing and error handling
- ✅ Help flag display
- ✅ Invalid argument rejection

### 2. Security Pipeline Tests (`tests/test_security_pipeline.py`) - 25 tests

Core security pipeline configuration validation:

**Reproducible Builds:**

- ✅ Build script exists and is executable
- ✅ SOURCE_DATE_EPOCH set for reproducibility
- ✅ Deterministic artifact generation (slow test)

**SBOM Generation:**

- ✅ Release workflow generates SBOM
- ✅ SBOM validation configured (CycloneDX format)

**Vulnerability Scanning:**

- ✅ OSV scanner configured in workflows
- ✅ Scheduled vulnerability scanning exists

**Attestation & Signing:**

- ✅ GitHub build provenance attestation configured
- ✅ Cosign keyless signing configured
- ✅ Minimal permissions enforced
- ✅ id-token: write permission for signing

**Workflow Security:**

- ✅ GitHub Actions pinned to SHAs (warns on tags)
- ✅ Harden-runner configured in release workflow
- ✅ No dangerous pull_request_target usage

**Verification:**

- ✅ Build verification script exists and is executable
- ✅ Provenance verification script exists
- ✅ Scripts use GitHub CLI for attestation verification

**Rebuilder Workflow:**

- ✅ Rebuilder workflow exists for reproducibility checks
- ✅ Hash comparison configured

**Supply Chain Metadata:**

- ✅ SUPPLY-CHAIN.md documentation exists
- ✅ Verification instructions included
- ✅ pyproject.toml has required metadata

**Secrets Protection:**

- ✅ .gitignore excludes sensitive files (.env, *.pem,*.key)
- ✅ No hardcoded tokens in workflows

**Dependency Management:**

- ✅ requirements.in exists for dependency tracking
- ✅ Python version constraints specified

### 3. Cryptographic Integrity Tests (`tests/test_cryptographic_integrity.py`) - 30 tests

Deep validation of cryptographic operations and security hardening:

**Cosign Configuration (5 tests):**

- ✅ Keyless signing only (no private keys in repo)
- ✅ Rekor transparency log enabled (not disabled)
- ✅ Fulcio certificate authority used
- ✅ Correct OIDC issuer for GitHub Actions
- ✅ Certificate identity validation in verification

**Checksum Security (2 tests):**

- ✅ SHA-256 algorithm used (no weak hashes like MD5/SHA1)
- ✅ Checksums file itself is signed

**Attestation Security (3 tests):**

- ✅ Build provenance attestation configured
- ✅ All release artifacts attested
- ✅ SLSA provenance format generated

**Permission Hardening (4 tests):**

- ✅ Minimal permissions principle enforced
- ✅ No write-all permissions granted
- ✅ id-token: write only in appropriate workflows
- ✅ contents: write only for releases

**Secrets Handling (2 tests):**

- ✅ No secrets committed to repo (scans for common patterns)
- ✅ Secrets from GitHub Secrets, not hardcoded

**Dependency Integrity (3 tests):**

- ✅ No pip install without verification
- ✅ GitHub Actions pinned to full commit SHAs
- ✅ Requirements file integrity (no suspicious packages)

**Supply Chain Security (4 tests):**

- ✅ No downloads from untrusted HTTP sources
- ✅ Runner environment isolation (persist-credentials: false)
- ✅ No arbitrary code execution from PRs
- ✅ Environment protection for releases

**SBOM Quality (3 tests):**

- ✅ Standard format used (CycloneDX or SPDX)
- ✅ All dependencies included
- ✅ SBOM uploaded with release

**Reproducibility Guarantees (3 tests):**

- ✅ SOURCE_DATE_EPOCH set
- ✅ Locale environment fixed (LC_ALL, LANG, TZ)
- ✅ PYTHONHASHSEED set to 0

### 4. Runtime Security Tests (`tests/test_runtime_security.py`) - 12 tests

Runtime security properties of the built application:

**PYZ Security (3 tests):**

- ✅ Secure Python shebang (skipped until build)
- ✅ No bytecode cache pollution (skipped until build)
- ✅ Runs without write access to directory (skipped until build)

**Dependency Isolation (1 test):**

- ✅ No system package pollution (skipped until build)

**Input Validation (2 tests):**

- ✅ No shell injection vulnerabilities (skipped until build)
- ✅ Path traversal protection in build scripts

**Error Handling (2 tests):**

- ✅ No stack traces in normal errors (skipped until build)
- ✅ No sensitive info in version output (skipped until build)

**File Permissions (1 test):**

- ✅ Build outputs have secure permissions (skipped until build)

**Network Security (1 test):**

- ✅ Basic usage works without network (skipped until build)

**Code Integrity (2 tests):**

- ✅ PYZ is valid ZIP file (skipped until build)
- ✅ PYZ contains only expected files (skipped until build)

## Running the Tests

### Fast Tests Only (< 1 second)

```bash
uv run pytest tests/ -v -m "not slow"
```

### All Tests (including slow build tests)

```bash
uv run pytest tests/ -v
```

### Specific Test Category

```bash
# Security pipeline only
uv run pytest tests/test_security_pipeline.py -v

# Cryptographic integrity only
uv run pytest tests/test_cryptographic_integrity.py -v

# Runtime security only
uv run pytest tests/test_runtime_security.py -v

# CLI functionality only
uv run pytest tests/test_cli.py -v
```

### With Coverage

```bash
uv run pytest tests/ --cov=src --cov-report=html
```

## What These Tests Validate

### Security Features Verified

1. **Cryptographic Signing**
   - Keyless cosign signing via Sigstore
   - Rekor transparency log entries
   - Fulcio certificate authority
   - No private keys in repository

2. **Build Attestations**
   - GitHub build provenance (SLSA format)
   - All artifacts attested
   - Certificate identity validation

3. **Reproducible Builds**
   - Deterministic output
   - SOURCE_DATE_EPOCH set
   - Fixed locale and environment
   - Hash verification

4. **SBOM & Vulnerability Scanning**
   - CycloneDX SBOM generation
   - OSV vulnerability scanning
   - Scheduled security scans
   - SBOM uploaded with releases

5. **Workflow Hardening**
   - Minimal permissions (least privilege)
   - Actions pinned to commit SHAs
   - Egress control (harden-runner)
   - No pull_request_target vulnerabilities
   - Environment protection for releases

6. **Secrets Protection**
   - No secrets in repository
   - GitHub Secrets for sensitive data
   - .gitignore protects credentials
   - No accidental leaks

7. **Supply Chain Security**
   - HTTPS-only downloads
   - No arbitrary code execution
   - Runner environment isolation
   - Dependency integrity

8. **Runtime Security**
   - Input validation (no shell injection)
   - Path traversal protection
   - Secure file permissions
   - No bytecode pollution
   - Works without network access

## Attack Vectors Prevented

These tests validate protection against:

- ✅ **Supply Chain Attacks** - Actions pinned, SBOM, attestations
- ✅ **Credential Theft** - No secrets in repo, environment isolation
- ✅ **Code Injection** - Input validation, no pull_request_target RCE
- ✅ **Man-in-the-Middle** - Keyless signing, transparency logs
- ✅ **Dependency Confusion** - Requirement tracking, vulnerability scanning
- ✅ **Build Tampering** - Reproducible builds, attestations, signatures
- ✅ **Privilege Escalation** - Minimal permissions, environment protection
- ✅ **Data Exfiltration** - Egress control, harden-runner

## Continuous Validation

These tests should be run:

- ✅ **On every PR** - Fast tests validate configuration
- ✅ **On main branch** - Full test suite including slow tests
- ✅ **On releases** - All tests must pass before publishing
- ✅ **Scheduled** - Weekly runs to catch configuration drift

## Test Failures

If a test fails, it indicates a security configuration issue:

1. **Cryptographic tests fail** → Signing/attestation misconfigured
2. **Permission tests fail** → Overly broad workflow permissions
3. **Secrets tests fail** → Potential credential exposure
4. **Supply chain tests fail** → Vulnerable to supply chain attacks
5. **Runtime tests fail** → Application has security vulnerabilities

**Never disable failing security tests.** Fix the underlying issue.

## Adding New Tests

When adding security features:

1. Add corresponding tests to validate the feature
2. Ensure tests fail when security is misconfigured
3. Document what attack vectors the feature prevents
4. Update this documentation

## Security Baseline

This test suite establishes a **security baseline** for the template. All projects using this template should:

1. Keep all security tests passing
2. Add project-specific security tests
3. Run tests in CI/CD pipeline
4. Review test failures immediately

## References

- [SLSA Build Levels](https://slsa.dev/spec/v1.0/levels)
- [Sigstore Documentation](https://docs.sigstore.dev/)
- [OpenSSF Best Practices](https://bestpractices.coreinfrastructure.org/)
- [GitHub Actions Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
