# Testing Releases Guide

This guide explains how to test the release process without affecting production channels.

## 🧪 Staging Release Strategy

### Recommended Approach: Use Pre-releases

GitHub supports pre-release tags that are marked as "not production-ready":

```bash
# Alpha releases (early testing)
v0.0.1-alpha.1
v0.0.1-alpha.2

# Beta releases (feature complete, testing)
v0.0.1-beta.1
v0.0.1-beta.2

# Release candidates (final testing)
v0.0.1-rc.1
v0.0.1-rc.2

# Production release
v0.1.0
```

## 🎯 Current Workflow Behavior with Pre-releases

### ✅ Works Automatically (Safe for Testing)

| Workflow | Behavior on Pre-release | Notes |
|----------|------------------------|-------|
| **PyPI Publish** | Publishes to TestPyPI + PyPI | ✅ TestPyPI is safe for testing |
| **Nix/Cachix** | Builds and caches | ✅ Safe, just adds to cache |
| **Docker GHCR** | Publishes with pre-release tags | ✅ Tagged as alpha/beta, not latest |
| **Main Verify** | Runs security checks | ✅ Always good to run |

### ⚠️ Affects Production (Use Carefully)

| Workflow | Behavior on Pre-release | Recommendation |
|----------|------------------------|----------------|
| **Homebrew Tap** | Updates tap with version | Skip for alpha, OK for beta/rc |
| **Snap Store** | Publishes to stable | Use edge/beta channel manually |

## 📝 Step-by-Step: Test Release

### Option 1: Alpha Pre-release (Safest)

```bash
# 1. Create and push tag
git tag v0.0.1-alpha.1
git push origin v0.0.1-alpha.1

# 2. Create release on GitHub
gh release create v0.0.1-alpha.1 \
  --title "v0.0.1-alpha.1 - Test Release" \
  --notes "Testing release automation" \
  --prerelease

# 3. Watch workflows run
gh run list --limit 10

# 4. Test installations
# PyPI (from TestPyPI)
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    provenance-demo==0.0.1a1

# Docker (pre-release tag)
docker pull ghcr.io/redoubt-cysec/provenance-demo:0.0.1-alpha.1
```

### Option 2: Manual Workflow Triggers (No Release)

Test individual workflows without creating a release:

```bash
# 1. Go to GitHub Actions
open https://github.com/redoubt-cysec/provenance-template/actions

# 2. Choose workflow (e.g., "Publish to PyPI")
# 3. Click "Run workflow"
# 4. Fill in version and options
# 5. Watch it run
```

**Workflows that support manual trigger:**
- ✅ PyPI Publish (can choose TestPyPI only)
- ✅ Snap Publish (can choose edge channel)
- ✅ Docker Multi-arch
- ✅ Homebrew Tap

### Option 3: Start with v0.0.1 (Low-risk)

Start with a low version number:

```bash
# Create v0.0.1 as first "real" release
git tag v0.0.1
git push origin v0.0.1

gh release create v0.0.1 \
  --title "v0.0.1 - Initial Release" \
  --notes "First release for testing"

# Later bump to v0.1.0 when ready for "official" launch
git tag v0.1.0
git push origin v0.1.0
```

## 🔍 Monitoring Release Workflows

### Watch All Workflows

```bash
# List recent runs
gh run list --limit 20

# Watch specific workflow
gh run watch

# View logs for failed run
gh run view 123456789 --log-failed
```

### Check Published Artifacts

```bash
# PyPI/TestPyPI
open https://test.pypi.org/project/provenance-demo/
open https://pypi.org/project/provenance-demo/

# Docker GHCR
open https://github.com/redoubt-cysec/provenance-template/pkgs/container/provenance-demo

# Homebrew
open https://github.com/redoubt-cysec/homebrew-tap

# Snap Store
snapcraft status provenance-demo
```

## 🛡️ Pre-release Checklist

Before creating your first release (even alpha), verify:

```bash
# ✅ All secrets are set
gh secret list --repo redoubt-cysec/provenance-template

# Should see:
# - CACHIX_AUTH_TOKEN
# - CACHIX_CACHE_NAME
# - HOMEBREW_TAP_REPO
# - PYPI_TOKEN
# - TAP_GITHUB_TOKEN
# - TESTPYPI_TOKEN
# (SNAPCRAFT_STORE_CREDENTIALS - optional)

# ✅ Main branch builds successfully
gh run list --workflow="Main — Pre-release Security Gates" --limit 1

# ✅ Tests pass
gh run list --workflow="Test Coverage" --limit 1
```

## 🎬 Workflow Execution Order

When you create a release, workflows run in parallel:

```
Release Created (v0.0.1-alpha.1)
├─ Main Verify ✓ (runs first, ~2 min)
├─ PyPI Publish ✓ (~3 min)
│  ├─ Build packages
│  ├─ Publish to TestPyPI ✓
│  └─ Publish to PyPI ✓
├─ Docker Multi-arch ✓ (~5 min)
│  ├─ Build amd64 image
│  ├─ Build arm64 image
│  └─ Push to GHCR ✓
├─ Homebrew Tap ✓ (~3 min)
│  ├─ Download .pyz
│  ├─ Update formula
│  └─ Push to tap repo ✓
├─ Nix/Cachix ✓ (~4 min)
│  ├─ Build with Nix
│  └─ Push to Cachix ✓
└─ Snap Store ⏩ (skipped - no credentials yet)
```

## 🧹 Cleanup After Testing

### Delete Test Release

```bash
# Delete release and tag
gh release delete v0.0.1-alpha.1 --yes
git push --delete origin v0.0.1-alpha.1
git tag -d v0.0.1-alpha.1
```

### Remove Test Packages

**TestPyPI:** Can't delete, but that's OK - it's for testing
**PyPI:** Can't delete (by policy), use yanked versions:
```bash
# Mark as yanked (hidden from pip install)
twine yank --repository pypi provenance-demo 0.0.1-alpha.1
```

**Docker:** Delete image
```bash
# Via GitHub UI or:
gh api -X DELETE /user/packages/container/provenance-demo/versions/VERSION_ID
```

## 💡 Recommendations

### For First-Time Testing

1. **Use v0.0.1-alpha.1** as first test release
2. **Skip Snap** (optional, requires credentials)
3. **Let everything else run** (safe)
4. **Verify installations work** from each channel
5. **Delete and iterate** until satisfied
6. **Create v0.1.0** as official first release

### Channel Strategy

- **Alpha** (`v0.0.x-alpha.x`): Internal testing, TestPyPI only
- **Beta** (`v0.0.x-beta.x`): Limited testing, all channels
- **RC** (`v0.0.x-rc.x`): Final testing, all channels
- **Stable** (`v0.1.0+`): Production, all channels

## 🎯 Quick Test Command

Create an alpha release and watch:

```bash
#!/bin/bash
VERSION="v0.0.1-alpha.1"

# Create tag and release
git tag $VERSION
git push origin $VERSION

gh release create $VERSION \
  --title "$VERSION - Test Release" \
  --notes "Testing release automation pipeline" \
  --prerelease

# Watch workflows
echo "Watching workflows..."
gh run list --limit 10

echo ""
echo "Monitor at: https://github.com/redoubt-cysec/provenance-template/actions"
echo ""
echo "When done testing, cleanup with:"
echo "  gh release delete $VERSION --yes"
echo "  git push --delete origin $VERSION"
echo "  git tag -d $VERSION"
```

Save as `scripts/test-release.sh` and run:
```bash
chmod +x scripts/test-release.sh
./scripts/test-release.sh
```
