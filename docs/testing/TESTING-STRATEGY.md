# Testing Strategy

This document explains the complete testing approach for secure distribution.

## Three-Phase Testing

> **Automation tip:** Every distribution channel mentioned below has a dedicated harness in `scripts/distribution-testing/` plus the `distribution-testing.yml` GitHub Action. Run them locally to exercise dry-run installs before committing to a public release.

### Phase 1: Pre-Release Validation ✅

**File:** `tests/test_distribution_validation.py`

**Purpose:** Catch errors BEFORE publishing

**Tests:**

- ✅ Homebrew formula syntax valid
- ✅ Snap snapcraft.yaml structure correct
- ✅ PyPI metadata complete (pyproject.toml)
- ✅ Wheel/sdist build successfully
- ✅ .pyz has correct shebang and permissions
- ✅ Documentation includes installation instructions

**When:** Run on every PR and before tagging releases

**Runtime:** ~2-5 seconds

```bash
# Run validation tests
pytest tests/test_distribution_validation.py -v
```

**Why:** Prevents releasing broken configurations

---

### Phase 2: Local Integration Testing ✅

**File:** `tests/test_distribution_integration.py`

**Purpose:** Verify built artifacts work on clean systems

**Tests:**

- ✅ .pyz executes on Ubuntu, Debian, Fedora, Alpine, macOS, Windows
- ✅ Wheel installs via pip in virtual environments
- ✅ pipx installation works
- ✅ Cross-Python version compatibility (3.11, 3.12+)
- ✅ Artifact integrity (valid ZIP, proper structure)

**When:** Run before releases and weekly

**Runtime:** ~15-20 minutes (parallel in CI)

```bash
# Docker-based (fast, in CI)
pytest tests/test_distribution_integration.py::TestDirectPyzInstallation -v

# Multipass-based (comprehensive, local)
pytest tests/test_distribution_integration.py -v -s -m integration
```

**Why:** Ensures artifacts are functional before distribution

---

### Phase 3: Post-Release Verification ✅

**File:** `tests/test_published_distributions.py`

**Purpose:** Test ACTUAL published packages work

**Tests:**

- ✅ GitHub release exists and is downloadable
- ✅ Attestations verify correctly
- ✅ Checksums match downloaded artifacts
- ✅ Homebrew tap installs successfully (`brew install OWNER/tap/client`)
- ✅ PyPI package installs (`pip install package-name`)
- ✅ Complete end-to-end user workflow

**When:** Run AFTER publishing a release

**Runtime:** ~10-20 minutes

```bash
# Test specific release
pytest tests/test_published_distributions.py -v \
  --release-tag=v1.0.0 \
  --github-repo=Borduas-Holdings/redoubt-release-template

# Test latest release
pytest tests/test_published_distributions.py -v --use-latest \
  --github-repo=Borduas-Holdings/redoubt-release-template

# Set environment for tap/PyPI
export HOMEBREW_TAP="OWNER/tap"
export PYPI_PACKAGE="your-package-name"
pytest tests/test_published_distributions.py -v --use-latest
```

**Why:** Validates actual user experience works as expected

---

## Complete Testing Flow

```
┌─────────────────────────────────────────────┐
│ Developer writes code                        │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│ PR: Run security + validation tests         │
│ • test_security_pipeline.py                 │
│ • test_cryptographic_integrity.py           │
│ • test_distribution_validation.py           │
│ Runtime: ~1 second                          │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│ Main: Run full unit test suite             │
│ • All fast tests                            │
│ • SBOM + OSV scans                          │
│ Runtime: ~2 minutes                         │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│ Before Release: Integration tests           │
│ • test_distribution_integration.py          │
│ • Docker containers (6 platforms)           │
│ Runtime: ~15 minutes                        │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│ Tag Release: v1.0.0                         │
│ • Runs secure release workflow              │
│ • Builds + signs + attests                  │
│ • Publishes to GitHub Releases              │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│ After Release: Verify published packages    │
│ • test_published_distributions.py           │
│ • Test actual Homebrew install              │
│ • Test actual PyPI install                  │
│ • Test GitHub download + verify             │
│ Runtime: ~10-20 minutes                     │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│ Optional: Update taps/registries            │
│ • Homebrew tap workflow runs                │
│ • Winget PR created                         │
│ • Snap store publication (if configured)    │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│ Weekly: Scheduled tests                     │
│ • Re-run published distribution tests       │
│ • Catch platform drift                      │
│ • Verify old releases still work            │
└─────────────────────────────────────────────┘
```

## Test Matrix

| Test Type | What It Tests | When It Runs | Speed | Requires |
|-----------|---------------|--------------|-------|----------|
| **Validation** | Config syntax, metadata | Every PR | ~2s | Nothing |
| **Security** | Crypto, supply chain, workflows | Every PR | ~0.3s | Nothing |
| **Local Integration** | Built artifacts work | Before release | ~15m | Built artifacts |
| **Published** | Real packages work | After release | ~10m | Published release |

## Environment Configuration

### For Local Testing

```bash
# Required for all tests
export GITHUB_REPO="Borduas-Holdings/redoubt-release-template"

# Optional for Homebrew tests
export HOMEBREW_TAP="OWNER/tap"

# Optional for PyPI tests
export PYPI_PACKAGE="your-package-name"
```

### For CI/CD

Set these as repository secrets/variables:

- `GITHUB_REPO`: Repository name
- `HOMEBREW_TAP`: Tap name (if using)
- `TAP_PUSH_TOKEN`: Token for updating tap
- `PYPI_TOKEN`: Token for publishing to PyPI (if using)

## Best Practices

### Before Every Release

1. **Run validation tests:**

   ```bash
   pytest tests/test_distribution_validation.py -v
   ```

2. **Build artifacts:**

   ```bash
   ./scripts/build_pyz.sh
   python -m build
   ```

3. **Run integration tests:**

   ```bash
   # Quick Docker-based
   gh workflow run integration-tests.yml

   # Or comprehensive local
   pytest tests/test_distribution_integration.py -v -m "not slow"
   ```

4. **Tag and release:**

   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

### After Every Release

1. **Wait for workflows to complete** (~5-10 minutes)

2. **Run published distribution tests:**

   ```bash
   pytest tests/test_published_distributions.py -v \
     --release-tag=v1.0.0 \
     --github-repo=Borduas-Holdings/redoubt-release-template
   ```

3. **Manually verify one install method:**

   ```bash
   # Test Homebrew
   brew tap OWNER/tap
   brew install client

   # Or test direct download
   gh release download v1.0.0 --repo Borduas-Holdings/redoubt-release-template
   gh attestation verify client.pyz --repo Borduas-Holdings/redoubt-release-template
   ```

### During Development

- Run fast tests frequently: `pytest tests/ -m "not slow and not integration"`
- Run security tests before commit: `pytest tests/test_security_pipeline.py -v`
- Use pre-commit hooks: `pre-commit run --all-files`

## Troubleshooting

### Validation Tests Fail

**Problem:** Formula syntax invalid, metadata missing

**Solution:**

- Check formula syntax in [packaging/homebrew-tap/Formula/](packaging/homebrew-tap/Formula/)
- Verify [pyproject.toml](pyproject.toml) has all required fields
- Ensure placeholders (Borduas-Holdings/redoubt-release-template) are replaced

### Integration Tests Fail

**Problem:** Artifacts don't work on clean OS

**Solution:**

- Rebuild artifacts: `./scripts/build_pyz.sh`
- Check Python version compatibility
- Verify dependencies are included
- Test locally first: `python dist/client.pyz --version`

### Published Tests Fail

**Problem:** Can't download or install from real sources

**Solutions:**

- **Release doesn't exist:** Check GitHub releases page
- **Tap not found:** Verify tap repository exists and is public
- **PyPI 404:** Package not published yet or wrong name
- **Attestation fails:** Wait a few minutes for attestation to propagate

## Continuous Improvement

### Add New Tests

When adding a distribution channel:

1. Add validation test in `test_distribution_validation.py`
2. Add local integration test in `test_distribution_integration.py`
3. Add published test in `test_published_distributions.py`
4. Update this documentation

### Monitor Test Health

- Track test runtime (should stay fast)
- Watch for flaky tests (especially network-dependent)
- Update tests when platforms change
- Add regression tests for bugs

## Summary

**Total test coverage:**

- ✅ **40+ validation tests** - Config correctness
- ✅ **67 security tests** - Security properties
- ✅ **24+ integration tests** - Cross-platform functionality
- ✅ **15+ published tests** - Real-world user experience

**Total: 145+ tests** covering the complete software supply chain from development through distribution.

This ensures your CLI is:

1. ✅ Securely built and signed
2. ✅ Works on all platforms
3. ✅ Actually installable by users
4. ✅ Verifiable end-to-end
