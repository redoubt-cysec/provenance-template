# Complete Security Checklist

This document provides a comprehensive security checklist for using this template.

## 🎯 Initial Setup (Before First Release)

### Repository Configuration

- [ ] Replace `Borduas-Holdings/redoubt-release-template` with your actual GitHub org/repo
- [ ] Replace `<PINNED_SHA>` with actual commit SHAs in all workflows
- [ ] Replace `<PINNED_DIGEST>` with actual image digests (if using OCI)
- [ ] Update `[YOUR_SECURITY_EMAIL]` in SECURITY.md
- [ ] Update package name in pyproject.toml
- [ ] Update CLI entry point and artifact names

### GitHub Security Settings

- [ ] Enable branch protection for `main`:
  - Require pull request reviews (at least 1)
  - Require status checks to pass
  - Require signed commits (optional but recommended)
  - Include administrators
  - Restrict force pushes
  - Restrict deletions
- [ ] Enable tag protection for `v*` pattern:
  - Block tag creation by non-admins (optional)
  - Require signed tags (optional)
- [ ] Enable GitHub Advanced Security (if available):
  - Dependabot alerts
  - Dependabot security updates
  - Secret scanning
  - Code scanning (CodeQL)
- [ ] Create GitHub environment for releases:
  - Name: `production`
  - Protection rules: Required reviewers
  - Environment secrets (if needed)

### Secrets Configuration

Required secrets (if using distribution channels):

- [ ] `TAP_PUSH_TOKEN` - GitHub PAT with write access to homebrew-tap repo
- [ ] `WINGET_GITHUB_TOKEN` - GitHub PAT with PR access to microsoft/winget-pkgs

Verify secrets are NOT committed:

- [ ] Run: `uv run pytest tests/test_cryptographic_integrity.py::TestSecretsHandling -v`
- [ ] Check .gitignore includes .env, *.pem,*.key
- [ ] Scan repository: `git secrets --scan` (if installed)

### Pre-commit Hooks

- [ ] Install pre-commit: `pip install pre-commit`
- [ ] Initialize hooks: `pre-commit install`
- [ ] Run all hooks: `pre-commit run --all-files`
- [ ] Generate secrets baseline: `detect-secrets scan > .secrets.baseline`

### Dependency Management

- [ ] Review requirements.in for unnecessary dependencies
- [ ] Enable Dependabot (already configured in .github/dependabot.yml)
- [ ] Consider using Renovate as alternative
- [ ] Set up automated dependency updates

## 🔒 Security Validation (Run These Tests)

### Fast Security Tests (< 1 second)

```bash
# All fast tests
uv run pytest tests/ -m "not slow" -v

# By category
uv run pytest tests/test_cryptographic_integrity.py -v
uv run pytest tests/test_security_pipeline.py -v
uv run pytest tests/test_cli.py -v
```

### Comprehensive Tests (includes slow build tests)

```bash
# Full test suite
uv run pytest tests/ -v

# Runtime security (requires build)
uv run pytest tests/test_runtime_security.py -v
```

### Expected Results

- ✅ **67 tests should PASS** (fast tests)
- ⏭️ **6 tests SKIPPED** (runtime tests, require build)
- 🐌 **6 tests DESELECTED** (slow tests, excluded by default)
- ❌ **0 tests should FAIL**

If any tests fail, **DO NOT proceed** until fixed.

## 🔐 Cryptographic Security Checklist

### Keyless Signing (Cosign)

- [ ] Verify `COSIGN_EXPERIMENTAL=1` in release workflow
- [ ] Verify NO private keys in repository
- [ ] Verify Rekor transparency log enabled (not disabled)
- [ ] Verify Fulcio CA configured
- [ ] Verify OIDC issuer: `https://token.actions.githubusercontent.com`
- [ ] Test: `pytest tests/test_cryptographic_integrity.py::TestCosignConfiguration -v`

### Build Attestations

- [ ] Verify `actions/attest-build-provenance` in release workflow
- [ ] Verify attestations for all artifacts
- [ ] Verify SLSA provenance format
- [ ] Test: `pytest tests/test_cryptographic_integrity.py::TestAttestationSecurity -v`

### Checksums

- [ ] Verify SHA-256 used (not MD5/SHA1)
- [ ] Verify SHA256SUMS file is signed
- [ ] Test: `pytest tests/test_cryptographic_integrity.py::TestChecksumSecurity -v`

## 🛡️ Supply Chain Security Checklist

### GitHub Actions

- [ ] All actions pinned to commit SHAs (not tags)
- [ ] Harden-runner configured with egress-policy
- [ ] No pull_request_target with PR code checkout
- [ ] Minimal permissions (contents: read by default)
- [ ] Test: `pytest tests/test_cryptographic_integrity.py::TestSupplyChainSecurity -v`

### Dependencies

- [ ] requirements.in lists all direct dependencies
- [ ] No suspicious packages
- [ ] Vulnerability scanning enabled (OSV)
- [ ] License compliance checked
- [ ] Test: `pytest tests/test_cryptographic_integrity.py::TestDependencyIntegrity -v`

### SBOM

- [ ] CycloneDX format configured
- [ ] All dependencies included
- [ ] SBOM uploaded with releases
- [ ] Test: `pytest tests/test_cryptographic_integrity.py::TestSBOMQuality -v`

## ⚙️ Workflow Security Checklist

### Permissions

- [ ] Minimal permissions principle enforced
- [ ] No `write-all` permissions
- [ ] `id-token: write` only where needed
- [ ] `contents: write` only in release workflow
- [ ] Test: `pytest tests/test_cryptographic_integrity.py::TestPermissionHardening -v`

### Environment Isolation

- [ ] `persist-credentials: false` in checkouts
- [ ] Environment protection for releases
- [ ] No credentials in environment variables
- [ ] Test: `pytest tests/test_security_pipeline.py::TestWorkflowSecurity -v`

### Secrets Handling

- [ ] No secrets committed to repository
- [ ] GitHub Secrets used for sensitive data
- [ ] .gitignore protects credentials
- [ ] Test: `pytest tests/test_cryptographic_integrity.py::TestSecretsHandling -v`

## 🔨 Build Security Checklist

### Reproducibility

- [ ] SOURCE_DATE_EPOCH set in build
- [ ] Fixed locale (LC_ALL, LANG, TZ)
- [ ] PYTHONHASHSEED=0
- [ ] Deterministic build verified
- [ ] Test: `pytest tests/test_cryptographic_integrity.py::TestReproducibilityGuarantees -v`

### Build Environment

- [ ] No build caches in release workflow
- [ ] Clean environment for each build
- [ ] No write access to source during build
- [ ] Test: `pytest tests/test_security_pipeline.py::TestReproducibleBuilds -v`

## 🏃 Runtime Security Checklist

### Input Validation

- [ ] No shell injection vulnerabilities
- [ ] Path traversal protection
- [ ] Argument parsing validates input
- [ ] Test: `pytest tests/test_runtime_security.py::TestInputValidation -v`

### Application Security

- [ ] Secure file permissions
- [ ] No bytecode cache pollution
- [ ] Works without network access
- [ ] No sensitive info in error messages
- [ ] Test: `pytest tests/test_runtime_security.py -v`

## 📋 Pre-Release Checklist

Before cutting a release:

### Code Quality

- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] Pre-commit hooks pass: `pre-commit run --all-files`
- [ ] No security warnings: `bandit -r src/`
- [ ] License check passes: `./scripts/check_licenses.sh`

### Security Scans

- [ ] Vulnerability scan clean: `osv-scanner --lockfile requirements.txt`
- [ ] Secret scan clean: `detect-secrets scan`
- [ ] No hardcoded credentials
- [ ] SBOM generated successfully

### Verification Scripts

- [ ] Build verification script works: `./scripts/verify_build.sh`
- [ ] Provenance verification script works: `./scripts/verify_provenance.sh`
- [ ] Both scripts executable and tested

### Documentation

- [ ] CHANGELOG.md updated (if maintained)
- [ ] Version bumped in pyproject.toml
- [ ] README.md reflects current version
- [ ] SECURITY.md is current

## 🚀 Release Process

### Create Release

```bash
# 1. Ensure on main branch
git checkout main
git pull origin main

# 2. Run full test suite
uv run pytest tests/ -v

# 3. Tag release (semantic versioning)
git tag v1.0.0
git push origin v1.0.0

# 4. Monitor release workflow
# GitHub → Actions → Secure Release
```

### Post-Release Verification

- [ ] Download release artifacts
- [ ] Verify attestations: `gh attestation verify artifact.pyz --repo Borduas-Holdings/redoubt-release-template`
- [ ] Verify checksums: `sha256sum --check SHA256SUMS`
- [ ] Verify signature: `cosign verify-blob ... SHA256SUMS`
- [ ] Test artifact works: `./artifact.pyz --version`
- [ ] Check SBOM included in release
- [ ] Check vulnerability report clean

### Distribution (Optional)

If using Homebrew tap:

- [ ] Tap workflow succeeded
- [ ] Formula updated in homebrew-tap repo
- [ ] Test: `brew install OWNER/tap/app`

If using Winget:

- [ ] Winget PR created automatically
- [ ] PR follows winget guidelines
- [ ] Test after merge: `winget install OWNER.APP`

If using OCI:

- [ ] Image pushed to GHCR
- [ ] Image signed with cosign
- [ ] SBOM attached to image
- [ ] Test: `docker pull ghcr.io/Borduas-Holdings/redoubt-release-template:tag`

## 🔄 Ongoing Maintenance

### Weekly

- [ ] Review Dependabot PRs
- [ ] Check Scorecard results
- [ ] Review security alerts
- [ ] Run scheduled scans

### Monthly

- [ ] Update pinned action SHAs
- [ ] Review workflow configurations
- [ ] Update documentation
- [ ] Run full test suite on latest release

### Quarterly

- [ ] Security audit of workflows
- [ ] Review and update SECURITY.md
- [ ] Test verification scripts
- [ ] Review dependency licenses

## 🚨 Security Incident Response

If a security issue is discovered:

1. **Assess Impact**
   - Which versions affected?
   - What is the severity?
   - Is it being actively exploited?

2. **Immediate Actions**
   - Create security advisory (GitHub)
   - Notify users if critical
   - Work on patch privately

3. **Fix & Release**
   - Develop fix in private fork
   - Test thoroughly
   - Create security release
   - Publish advisory

4. **Post-Incident**
   - Add regression test
   - Update security documentation
   - Review similar code patterns

## 📊 Compliance & Auditing

### SLSA Compliance

This template targets **SLSA Build Level 3**:

- ✅ Build service (GitHub Actions)
- ✅ Build as code (workflow defined)
- ✅ Ephemeral environment (clean runners)
- ✅ Isolated (harden-runner egress control)
- ✅ Parameterless (no external inputs in build)
- ✅ Hermetic (no cache, reproducible)
- ✅ Provenance (GitHub attestations)

### Security Standards

Aligned with:

- ✅ OpenSSF Best Practices
- ✅ NIST SSDF (Secure Software Development Framework)
- ✅ Sigstore/Cosign keyless signing
- ✅ SLSA provenance (in-toto format)
- ✅ CycloneDX SBOM specification
- ✅ OpenSSF Scorecards metrics

## ✅ Final Validation

Before considering setup complete:

```bash
# 1. Run complete test suite
uv run pytest tests/ -v

# Expected: 67 passed, 6 skipped, 6 deselected

# 2. Run pre-commit on all files
pre-commit run --all-files

# 3. Build and test locally
./scripts/build_pyz.sh
./dist/client.pyz --version

# 4. Verify deterministic build
./scripts/build_pyz.sh
sha256sum dist/client.pyz  # Note hash
rm -rf dist build
./scripts/build_pyz.sh
sha256sum dist/client.pyz  # Should match

# 5. Check for secrets
detect-secrets scan

# 6. License check
./scripts/check_licenses.sh
```

All checks should pass. If anything fails, **stop and fix** before releasing.

---

## 📚 Additional Resources

- [SECURITY.md](./SECURITY.md) - Security policy
- [SECURITY-TESTING.md](./SECURITY-TESTING.md) - Test documentation
- [Developer Guide](../contributing/DEVELOPER-GUIDE.md) - Customization guide
- [SUPPLY-CHAIN.md](./SUPPLY-CHAIN.md) - Verification instructions

---

**Remember:** Security is not a one-time setup. It requires ongoing vigilance and maintenance.
