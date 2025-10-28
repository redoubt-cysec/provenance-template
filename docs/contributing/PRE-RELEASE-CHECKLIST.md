# Pre-Release Checklist - Release-Ready Code

**Current Status:** ✅ Feature Complete, ⚠️ Needs Configuration

---

## 🚨 CRITICAL (Must Do Before Release)

### 1. ❌ Replace redoubt-cysec/provenance-demo Placeholders

**Status:** 74 instances found
**Impact:** BLOCKING - Code won't work without this

```bash
# Find all instances
grep -r "redoubt-cysec/provenance-demo" --include="*.yml" --include="*.yaml" --include="*.md" .

# Replace with your values
find .github scripts docs -type f \( -name "*.yml" -o -name "*.yaml" -o -name "*.md" \) -exec sed -i '' 's/OWNER\/REPO/yourusername\/your-repo/g' {} \;

# Or use interactive script
./scripts/setup_local_config.sh
```

**Files affected:**

- `.github/workflows/*.yml` - All GitHub Actions
- `docs/**/*.md` - Documentation examples
- `scripts/**/*.sh` - Test scripts
- `README.md`, `SUPPLY-CHAIN.md` - Main docs

### 2. ❌ Pin GitHub Action SHAs

**Status:** 47 instances of `<PINNED_SHA>` found
**Impact:** SECURITY RISK - Actions not pinned to specific commits

```bash
# Find all unpinned actions
grep -r "<PINNED_SHA>" .github/workflows/

# Pin each one manually:
# 1. Go to https://github.com/OWNER/ACTION/commits/main
# 2. Click on the latest commit
# 3. Copy the full SHA (40 characters)
# 4. Replace <PINNED_SHA> with that SHA

# Example:
# uses: actions/checkout@<PINNED_SHA>
# becomes:
# uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11
```

**Why:** Prevents supply chain attacks through compromised Actions

### 3. ❌ Add LICENSE File

**Status:** NO LICENSE file found
**Impact:** LEGAL - Cannot be used without license

```bash
# Choose a license (examples):
# - MIT (permissive)
# - Apache 2.0 (permissive with patent grant)
# - GPL-3.0 (copyleft)

# Create LICENSE file
# Use: https://choosealicense.com
```

**Recommendation:** MIT or Apache 2.0 for template repository

---

## ⚠️ IMPORTANT (Should Do)

### 4. ⚠️ Test All GitHub Workflows

**Status:** Workflows exist but not tested
**Impact:** May have errors in CI/CD

```bash
# Trigger workflows manually
gh workflow run integration-tests.yml
gh workflow run distribution-testing.yml
gh workflow run coverage.yml

# Or wait for first push to trigger them
```

### 5. ⚠️ Verify No Secrets in Repository

**Status:** Should verify before public release

```bash
# If you have detect-secrets
detect-secrets scan

# Manual check
git grep -iE "(password|secret|api[_-]?key|token)" | grep -v "SECRET_NAME"

# Check for accidentally committed files
git log --all --full-history -- "*.pem" "*.key" ".env"
```

### 6. ⚠️ Update pyproject.toml Metadata

**Status:** May have template values

```bash
# Edit pyproject.toml
# Update:
#   - name = "demo-secure-cli" → your package name
#   - authors = [...]
#   - description = "..."
#   - [project.urls] - Your URLs
#   - [project.scripts] - Your CLI command name
```

### 7. ⚠️ Run Full Test Suite

**Status:** Should pass before release

```bash
# Run all tests
uv run pytest tests/ -v

# Expected: All tests pass
# Watch for:
#   - test_verification_enforcement.py MUST pass
#   - No failures in security tests
#   - Placeholder checks may fail (expected until redoubt-cysec/provenance-demo replaced)
```

---

## 📋 RECOMMENDED (Nice to Have)

### 8. 📋 Add CHANGELOG.md

```bash
# Create CHANGELOG.md
cat > CHANGELOG.md << 'EOF'
# Changelog

## [Unreleased]

### Added
- Comprehensive Phase 1 & Phase 2 testing framework
- Attestation verification in all distribution tests
- Docker fallback for Linux package managers on macOS
- Organized packaging/ structure

### Changed
- Renamed distribution-testing to phase1-testing
- Organized documentation by category

### Fixed
- All ARM architecture issues (Conda, Terraform)
- Infinite loop bugs in test runners
- Python 3.11+ compatibility

## [1.0.0] - 2025-10-18

Initial release
EOF
```

### 9. 📋 Add CODE_OF_CONDUCT.md

```bash
# Use GitHub's template or Contributor Covenant
# https://www.contributor-covenant.org/
```

### 10. 📋 Add Issue/PR Templates

```bash
mkdir -p .github/ISSUE_TEMPLATE
# Add bug report template
# Add feature request template
# Add PR template
```

### 11. 📋 Add Badges to README

```markdown
[![Tests](https://github.com/redoubt-cysec/provenance-demo/workflows/Tests/badge.svg)](https://github.com/redoubt-cysec/provenance-demo/actions)
[![Coverage](https://img.shields.io/codecov/c/github/redoubt-cysec/provenance-demo)](https://codecov.io/gh/redoubt-cysec/provenance-demo)
[![License](https://img.shields.io/github/license/redoubt-cysec/provenance-demo)](LICENSE)
```

---

## 🧪 VERIFICATION STEPS

### Pre-Commit Verification

```bash
# 1. Check git status
git status

# 2. Verify no secrets
git diff --cached | grep -iE "password|secret|token" | grep -v "SECRET_NAME"

# 3. Run tests
uv run pytest tests/ -m "not slow and not integration"

# 4. Run security checks
uv run pytest tests/test_security_pipeline.py -v
uv run pytest tests/test_verification_enforcement.py -v

# 5. Run Phase 1 tests
./scripts/phase1-testing/run-all.sh

# 6. Verify documentation
ls -la docs/
```

### Post-Commit Verification

```bash
# 1. Push to GitHub
git push origin main

# 2. Watch GitHub Actions
gh run list --limit 5

# 3. Verify workflows pass
gh run watch

# 4. Check for issues
gh issue list
```

---

## 📊 CURRENT STATUS AUDIT

### ✅ COMPLETE

- [x] Directory structure organized (packaging/)
- [x] Testing framework (Phase 1 & Phase 2)
- [x] Verification integrated (all 14 tests)
- [x] Meta-test enforcement
- [x] Documentation organized
- [x] .gitignore comprehensive
- [x] Security verification code (production-grade)
- [x] Auto-install script
- [x] All bugs fixed

### ❌ BLOCKING (Must fix before release)

- [ ] **Replace redoubt-cysec/provenance-demo** (74 instances)
- [ ] **Pin GitHub Action SHAs** (47 instances)
- [ ] **Add LICENSE file** (critical!)

### ⚠️ IMPORTANT (Should fix)

- [ ] Test GitHub workflows
- [ ] Update pyproject.toml metadata
- [ ] Run full test suite
- [ ] Verify no secrets

### 📋 OPTIONAL (Nice to have)

- [ ] Add CHANGELOG.md
- [ ] Add CODE_OF_CONDUCT.md
- [ ] Add issue templates
- [ ] Add badges to README

---

## 🎯 QUICKEST PATH TO RELEASE

### Minimum Steps (1-2 hours)

```bash
# 1. Add LICENSE (5 minutes)
cat > LICENSE << 'EOF'
MIT License
Copyright (c) 2025 Your Name
...
EOF

# 2. Replace redoubt-cysec/provenance-demo (10 minutes)
./scripts/setup_local_config.sh  # Interactive
# OR
find . -type f -name "*.yml" -o -name "*.md" | xargs sed -i '' 's/OWNER\/REPO/yourusername\/your-repo/g'

# 3. Pin Action SHAs (30-60 minutes)
# Manually pin each <PINNED_SHA> in .github/workflows/*.yml
# Use: https://github.com/OWNER/ACTION/commits/main

# 4. Update pyproject.toml (5 minutes)
# Edit: name, authors, description, URLs

# 5. Test (10 minutes)
uv run pytest tests/ -m "not slow"
./scripts/phase1-testing/run-all.sh

# 6. Commit & Push
git add .
git commit -m "Production-ready release"
git push origin main

# 7. Tag release
git tag v1.0.0 -m "First production release"
git push --tags
```

---

## 🚀 READY FOR RELEASE WHEN

- ✅ LICENSE file added
- ✅ redoubt-cysec/provenance-demo replaced (all 74 instances)
- ✅ GitHub Action SHAs pinned (all 47 instances)
- ✅ pyproject.toml updated
- ✅ Tests pass
- ✅ No secrets committed

**Then:** READY TO RELEASE! 🎉

---

## 📝 Quick Commands

```bash
# Check placeholders
grep -r "redoubt-cysec/provenance-demo" .github/ | wc -l
grep -r "<PINNED_SHA>" .github/ | wc -l

# Run critical tests
uv run pytest tests/test_verification_enforcement.py -v
uv run pytest tests/test_security_pipeline.py -v

# Verify ready
git status
git diff --stat
```

---

**Next Action:** Start with LICENSE, then redoubt-cysec/provenance-demo, then pin SHAs. That's the critical path to release!
