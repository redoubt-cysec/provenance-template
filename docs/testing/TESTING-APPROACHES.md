# Testing Approaches for Distribution Packages

This document explains how to test different distribution methods at various stages
(local, pre-release, and published).

## Overview: Three Testing Phases

### Automation Support 🚀

- **What:** The repo now includes CI-ready harnesses for every distribution surface listed in this guide.
- **Where:** See `.github/workflows/distribution-testing.yml` and `scripts/distribution-testing/`.
- **How:** Each script exercises the staging/private-testing mode for its channel and skips gracefully when a prerequisite tool is missing.
- **Run locally:** `bash scripts/distribution-testing/run-all.sh` (Linux/macOS) or `pwsh scripts/distribution-testing/chocolatey-local-feed.ps1` / `winget-local-manifest.ps1` (Windows).
- **Environment variables:** Set channel-specific overrides such as `GH_DRAFT_REPO` before running the matching script.

### Phase 1: Local Build Testing ✅ (Currently Implemented)

- **What:** Test that locally built artifacts work on fresh systems
- **When:** During development, before any release
- **How:** Copy built artifacts to VMs and test execution
- **Tests:** Binary compatibility, dependencies, execution

### Phase 2: Private Distribution Testing 🎯 ✅ (Implemented)

- **What:** Test package manager installation without public release
- **When:** After local build, before publishing
- **How:** Use private repositories, local servers, or test registries
- **Tests:** Installation flow, package manager integration
- **Scripts:** Automated setup and VM test scripts for all platforms

### Phase 3: Published Release Testing 📦 (Post-release)

- **What:** Test real installation from public registries
- **When:** After publishing to official stores
- **How:** Install from production registries
- **Tests:** End-to-end user experience

---

## Platform-by-Platform Testing Guide

### 🍺 Homebrew (Private Tap)

#### ✅ Phase 1: Local Build Testing (Current)

```bash
# Build locally
./scripts/build_pyz.sh

# Transfer to VM
multipass transfer dist/provenance-demo.pyz vm:/tmp/

# Test execution
ssh vm "chmod +x /tmp/provenance-demo.pyz && /tmp/provenance-demo.pyz --version"
```

**What this tests:** Binary works on macOS/Linux

#### 🎯 Phase 2: Private Tap Testing ✅ (Automated)

```bash
# Automated setup and testing:
./scripts/phase2-testing/setup-homebrew-tap.sh
./scripts/phase2-testing/test-homebrew-tap-vm.sh

# Or manually:
# 1. Create a private tap repository: OWNER/homebrew-tap
# 2. Add formula to that repo
# 3. In VM, install from YOUR tap (not central Homebrew)

# On your machine:
git clone https://github.com/OWNER/homebrew-tap
cp packaging/homebrew-tap/Formula/redoubt.rb homebrew-tap/Formula/
cd homebrew-tap
git add Formula/redoubt.rb
git commit -m "Add redoubt formula"
git push

# In VM:
brew tap OWNER/tap  # Points to YOUR repo, not central Homebrew
brew install redoubt
redoubt --version
```

**What this tests:**

- Homebrew can fetch from your tap
- Formula syntax is correct
- Dependencies resolve
- Installation completes
- Binary is accessible in PATH

**Key difference:** You're using YOUR tap (github.com/OWNER/homebrew-tap), not the central Homebrew registry.

#### 📦 Phase 3: Published Testing

```bash
# After submitting PR to homebrew/homebrew-core
brew install redoubt  # From central Homebrew
```

---

### 📦 PyPI (pip/pipx)

#### ✅ Phase 1: Local Build Testing (Current)

```bash
# Build wheel
./scripts/build_pyz.sh

# In VM:
pip install /tmp/redoubt_release_demo-0.1.0-py3-none-any.whl
redoubt --version
```

#### 🎯 Phase 2: Test PyPI ✅ (Automated)

```bash
# Automated setup and testing:
./scripts/phase2-testing/setup-test-pypi.sh
./scripts/phase2-testing/test-test-pypi-vm.sh

# Or manually:
# Upload to Test PyPI (separate from production PyPI)
twine upload --repository testpypi dist/*

# In VM:
pip install --index-url https://test.pypi.org/simple/ provenance-demo
redoubt --version
```

**What this tests:**

- Package uploads correctly
- Metadata is valid
- Installation from PyPI-like index works
- Dependencies resolve

**Key difference:** test.pypi.org is a separate testing instance.

#### 📦 Phase 3: Published Testing

```bash
# After uploading to production PyPI
pip install provenance-demo
```

---

### 📦 Snap

#### ✅ Phase 1: Local Build Testing (Current)

```bash
# Build snap
snapcraft

# Transfer to VM
multipass transfer provenance-demo_0.1.0_all.snap vm:/tmp/

# In VM:
sudo snap install --dangerous /tmp/provenance-demo_0.1.0_all.snap
redoubt --version
```

**What this tests:** Snap package builds and installs locally
**Note:** `--dangerous` flag bypasses signature checking for local testing

#### 🎯 Phase 2: Edge Channel Testing ✅ (Automated)

```bash
# Automated setup and testing:
./scripts/phase2-testing/setup-snap-edge.sh
./scripts/phase2-testing/test-snap-edge-vm.sh

# Or manually:
# Upload to edge channel (not visible to general users)
snapcraft upload provenance-demo_0.1.0_all.snap --release=edge

# In VM:
snap install provenance-demo --edge
```

**What this tests:**

- Upload to Snap Store works
- Package passes automatic checks
- Installation from store works
- Updates work

**Key difference:** Edge channel is for testing, not visible in default store search.

#### 📦 Phase 3: Published Testing

```bash
# After releasing to stable channel
snap install provenance-demo
```

---

### 🐳 Docker

#### ✅ Phase 1: Local Build Testing (Current) ✅ TESTED

```bash
# Build locally
docker build -t redoubt-test .

# Test
docker run redoubt-test --version
docker run redoubt-test hello world
docker run redoubt-test verify
```

**What this tests:** Container builds and runs

#### 🎯 Phase 2: Private Registry Testing ✅ (Automated)

```bash
# Automated setup and testing:
./scripts/phase2-testing/setup-docker-registry.sh
./scripts/phase2-testing/test-docker-registry-vm.sh

# Or manually:
# Push to GitHub Container Registry (private repo)
docker tag redoubt-test ghcr.io/OWNER/redoubt:test
docker push ghcr.io/OWNER/redoubt:test

# In VM:
docker pull ghcr.io/OWNER/redoubt:test
docker run ghcr.io/OWNER/redoubt:test --version
```

**What this tests:**

- Push to registry works
- Pull from registry works
- Image metadata correct

#### 📦 Phase 3: Published Testing

```bash
# After pushing to public Docker Hub
docker pull OWNER/redoubt
```

---

### 🪟 Windows Scoop

#### ✅ Phase 1: Local Build Testing (Current)

```powershell
# Download .pyz to Windows VM
curl -o provenance-demo.pyz https://yourserver/provenance-demo.pyz

# Test
python provenance-demo.pyz --version
```

#### 🎯 Phase 2: Private Bucket Testing ✅ (Automated)

```bash
# Automated setup:
./scripts/phase2-testing/setup-scoop-bucket.sh

# Then manually test in Windows VM:
# (Automated VM testing for Windows not yet implemented)

# In Windows PowerShell:
scoop bucket add OWNER https://github.com/OWNER/scoop-bucket
scoop install redoubt
redoubt --version
```

**What this tests:**

- Scoop can fetch from your bucket
- Manifest is valid
- Installation completes

**Key difference:** Using YOUR bucket, not the main Scoop bucket.

#### 📦 Phase 3: Published Testing

```powershell
# After submitting to official buckets
scoop bucket add extras
scoop install redoubt
```

---

### 📦 Debian/APT

#### ✅ Phase 1: Local Build Testing (Can add)

```bash
# Build .deb package
dpkg-buildpackage -us -uc

# In VM:
sudo dpkg -i provenance-demo_0.1.0-1_all.deb
redoubt --version
```

**What this tests:** Package builds and installs

#### 🎯 Phase 2: Private APT Repository ✅ (Automated)

```bash
# Automated setup and testing:
./scripts/phase2-testing/setup-apt-repo.sh
./scripts/phase2-testing/test-apt-repo-vm.sh

# Or manually:
# 1. Set up private APT repo (can use GitHub Pages)
# 2. Upload .deb to repo
# 3. In VM:

echo "deb [trusted=yes] https://OWNER.github.io/apt-repo stable main" | sudo tee /etc/apt/sources.list.d/redoubt.list
sudo apt update
sudo apt install redoubt
```

**What this tests:**

- APT repository setup works
- Package metadata is correct
- Dependencies resolve

#### 📦 Phase 3: Published Testing

```bash
# After adding to official Ubuntu/Debian repos or PPA
sudo add-apt-repository ppa:OWNER/redoubt
sudo apt install provenance-demo
```

---

### 📦 RPM (Fedora/RHEL)

#### ✅ Phase 1: Local Build Testing (Can add)

```bash
# Build RPM
rpmbuild -ba packaging/rpm/redoubt.spec

# In VM:
sudo rpm -i redoubt-0.1.0-1.rpm
redoubt --version
```

#### 🎯 Phase 2: Private YUM/DNF Repository ✅ (Automated)

```bash
# Automated setup and testing:
./scripts/phase2-testing/setup-rpm-repo.sh
./scripts/phase2-testing/test-rpm-repo-vm.sh

# Or manually:
# 1. Set up private YUM repo
# 2. Upload RPM
# 3. In VM:

sudo curl -fsSL https://OWNER.github.io/rpm-repo/redoubt.repo -o /etc/yum.repos.d/redoubt.repo
sudo dnf install redoubt
```

#### 📦 Phase 3: Published Testing

```bash
# After adding to EPEL or official repos
sudo dnf install provenance-demo
```

---

## Summary: What Each Phase Tests

### Phase 1: Local Build Testing ✅ (Current Implementation)

**Tests:**

- ✅ Binary executes on target OS
- ✅ Dependencies are satisfied
- ✅ Cross-platform compatibility
- ✅ Python version requirements
- ✅ File permissions correct

**Does NOT test:**

- ❌ Package manager installation flow
- ❌ Network download/fetch
- ❌ Repository metadata
- ❌ Update mechanisms
- ❌ Package signing/verification from store

**Current Status:** Implemented and working for:

- Homebrew (copy .pyz to VM)
- Snap (install with --dangerous flag)
- pip (install local wheel)
- pipx (install local wheel)
- Docker (local build and run)

---

### Phase 2: Private Distribution Testing 🎯 ✅ (Implemented)

**Tests:**

- ✅ Package manager can fetch from private repo
- ✅ Installation flow completes
- ✅ Dependencies resolve correctly
- ✅ Post-install scripts work
- ✅ Package appears in PATH
- ✅ Updates work (if testing update flow)

**Does NOT test:**

- ❌ Public discovery (search, browse)
- ❌ Central registry signing
- ❌ Official store policies
- ❌ Production CDN behavior

**Implemented for:**

- **Homebrew:** ✅ Create `OWNER/homebrew-tap` repo, test from there
- **PyPI:** ✅ Upload to test.pypi.org
- **Snap:** ✅ Use edge channel
- **Docker:** ✅ Push to private GHCR
- **Scoop:** ✅ Create private bucket repo (manual Windows testing)
- **APT:** ✅ Host on GitHub Pages
- **RPM:** ✅ Host on GitHub Pages

---

### Phase 3: Published Testing 📦 (Post-Release Only)

**Tests:**

- ✅ Everything from Phase 2, plus:
- ✅ Public discovery works
- ✅ Official signing/verification
- ✅ CDN distribution
- ✅ Update notifications
- ✅ Uninstall works

**Requires:**

- Published to official registries
- Review/approval processes completed
- Actual releases created

---

## 🚀 Automated Phase 2 Testing

### Master Test Runner

Run all Phase 2 tests with a single command:

```bash
# Run all platforms (with setup)
./scripts/phase2-testing/run-all-phase2-tests.sh --setup --all

# Run specific platforms
./scripts/phase2-testing/run-all-phase2-tests.sh --setup homebrew pypi docker

# Run tests only (no setup)
./scripts/phase2-testing/run-all-phase2-tests.sh homebrew snap
```

### Available Scripts

Each platform has two scripts:

1. **Setup script** - Creates private infrastructure and uploads package
2. **Test script** - Creates fresh VM and tests installation

| Platform | Setup Script | Test Script |
|----------|-------------|-------------|
| **Homebrew** | `setup-homebrew-tap.sh` | `test-homebrew-tap-vm.sh` |
| **PyPI** | `setup-test-pypi.sh` | `test-test-pypi-vm.sh` |
| **Docker** | `setup-docker-registry.sh` | `test-docker-registry-vm.sh` |
| **Snap** | `setup-snap-edge.sh` | `test-snap-edge-vm.sh` |
| **APT** | `setup-apt-repo.sh` | `test-apt-repo-vm.sh` |
| **RPM** | `setup-rpm-repo.sh` | `test-rpm-repo-vm.sh` |
| **Scoop** | `setup-scoop-bucket.sh` | (manual Windows testing) |

### Individual Platform Testing

Test a single platform:

```bash
# Setup infrastructure and upload
./scripts/phase2-testing/setup-homebrew-tap.sh

# Test in fresh VM
./scripts/phase2-testing/test-homebrew-tap-vm.sh
```

### What Gets Created

Phase 2 testing creates these private repositories:

- `OWNER/homebrew-tap` - Private Homebrew tap
- `OWNER/scoop-bucket` - Private Scoop bucket
- `OWNER/apt-repo` - APT repository (GitHub Pages)
- `OWNER/rpm-repo` - RPM repository (GitHub Pages)
- `ghcr.io/OWNER/redoubt:test-VERSION` - Docker test image
- Test PyPI package at test.pypi.org
- Snap edge channel (if registered)

All repositories are created automatically by the setup scripts.

---

## Current Testing Status

| Phase | Status | Coverage |
|-------|--------|----------|
| **Phase 1: Local Build** | ✅ Implemented | 7/7 VM tests passing |
| **Phase 2: Private Distribution** | ✅ Implemented | 6 platforms automated, 1 manual |
| **Phase 3: Published** | 📦 Post-release only | N/A |

### Phase 2 Platform Status

| Platform | Setup | VM Testing | Notes |
|----------|-------|-----------|-------|
| Homebrew | ✅ | ✅ | Creates private tap |
| PyPI | ✅ | ✅ | Uses test.pypi.org |
| Docker | ✅ | ✅ | GitHub Container Registry |
| Snap | ✅ | ✅ | Edge channel |
| APT | ✅ | ✅ | GitHub Pages hosting |
| RPM | ✅ | ✅ | GitHub Pages hosting |
| Scoop | ✅ | 🔧 | Windows VM testing manual |

**Phase 2 testing is now fully implemented!** This gives you complete pre-release testing without any public publication.
