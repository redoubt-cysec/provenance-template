# Testing Infrastructure Improvement Plan

**Status:** Revised after Critical Reassessment
**Created:** 2025-10-25
**Last Updated:** 2025-10-25 (Revised after discovering 4 missed platforms)

## ⚠️ CRITICAL UPDATE

**After reassessment, the initial analysis significantly understated the testing gaps.**

See [TESTING-REASSESSMENT.md](./TESTING-REASSESSMENT.md) for detailed findings.

## Executive Summary

This document outlines a prioritized plan to address gaps in the current testing infrastructure. Based on comprehensive analysis and subsequent reassessment:

**Revised Current State:**
- **21+ platforms** (not 17 as initially reported)
- ✅ 6 platforms with Phase 2 VM testing (PyPI, Homebrew, Docker, Snap, APT, RPM)
- ⚠️ 1 platform with partial testing (Flatpak: Phase 1 only, no Phase 2)
- ❌ 3 platforms with **ZERO testing** (AppImage, AUR, Nix Phase 1)
- ⚠️ 10 platforms with Phase 1 local simulation only
- ❌ 0 platforms with complete production-ready testing
- ❌ GPG signatures never tested (always bypassed)
- ❌ Real dependencies never tested (only mock packages)
- ❌ Single version/distro tested per platform
- ⚠️ Several simulators are suboptimal (PyPI uses basic http.server instead of devpi)

**Success Criteria for "Production Ready":**
1. All critical-path platforms (PyPI, APT, RPM, Homebrew, Docker) have GPG/signing
2. Multi-version testing for Python (3.9-3.12) and major Linux distros
3. Real dependency resolution tested (not mock packages)
4. Windows testing automated
5. At least one successful end-to-end release to production registries

---

## Priority Levels

- **P0 (Critical):** Blockers for GA release - must fix
- **P1 (High):** Major gaps that affect production deployments - should fix before GA
- **P2 (Medium):** Important improvements - can defer to post-GA
- **P3 (Low):** Nice-to-have enhancements - future work

---

## P0: Critical Priorities (Blockers for GA Release)

### P0.1: Add GPG Signature Support for APT/RPM

**Problem:**
Phase 2 testing bypasses signature verification with `[trusted=yes]` (APT) and `gpgcheck=0` (RPM). Production users cannot verify package authenticity.

**Impact:**
- Security: Users cannot verify packages haven't been tampered with
- Trust: Professional distributions require signed packages
- Compliance: Many enterprise environments require signature verification

**Solution:**
1. Generate GPG key pair for releases
2. Update APT setup script to sign repository metadata (Release, Release.gpg, InRelease)
3. Update RPM setup script to sign packages (rpm --addsign)
4. Update test scripts to import public key and verify signatures
5. Document key distribution process

**Success Criteria:**
- [ ] APT Phase 2 tests install with `gpgcheck=yes` and succeed
- [ ] RPM Phase 2 tests install with `gpgcheck=1` and succeed
- [ ] Documentation includes key management instructions
- [ ] Public key published to GitHub repo (keys/release.pub.asc)

**Estimated Effort:** 2-3 days

**Dependencies:** None

**Implementation Notes:**
```bash
# APT signing approach
gpg --gen-key  # Create key
gpg --export --armor > release.pub.asc
gpg --clearsign -o InRelease Release
gpg --detach-sign -o Release.gpg Release

# RPM signing approach
echo "%_gpg_name Release Key" >> ~/.rpmmacros
rpm --addsign *.rpm
```

**Files to Modify:**
- `scripts/phase2-testing/setup-apt-repo.sh`
- `scripts/phase2-testing/test-apt-repo-vm.sh`
- `scripts/phase2-testing/setup-rpm-repo.sh`
- `scripts/phase2-testing/test-rpm-repo-vm.sh`
- `docs/distribution/PLATFORM-SUPPORT.md`

---

### P0.2: Add Real Dependency Testing

**Problem:**
All test packages are mock/demo packages with no real dependencies. We never test if actual dependencies resolve correctly from public registries.

**Impact:**
- Risk: Production packages may fail to install due to dependency conflicts
- Risk: Transitive dependencies may be incompatible
- Risk: Version constraints may be too strict or too loose

**Solution:**
1. Update `pyproject.toml` with real dependencies (e.g., `click`, `rich`, `pyyaml`)
2. Update test packages to actually use these dependencies
3. Test installation pulls dependencies from real registries
4. Add dependency conflict testing (incompatible version ranges)

**Success Criteria:**
- [ ] PyPI Phase 2 tests pull 3+ real dependencies from pypi.org
- [ ] APT/RPM Phase 2 tests include system dependencies (e.g., python3-yaml)
- [ ] Docker Phase 2 tests include Python dependencies in requirements.txt
- [ ] Tests verify dependencies are actually imported and used

**Estimated Effort:** 1-2 days

**Dependencies:** None

**Implementation Notes:**
```toml
# Add to pyproject.toml
[project]
dependencies = [
    "click>=8.0",
    "rich>=13.0",
    "pyyaml>=6.0",
]
```

```python
# Update src/demo_cli/cli.py to use dependencies
import click
from rich.console import Console

@click.command()
def main():
    console = Console()
    console.print("[bold green]Dependencies working![/bold green]")
```

**Files to Modify:**
- `pyproject.toml`
- `src/demo_cli/cli.py`
- `scripts/phase2-testing/test-test-pypi-vm.sh` (verify deps installed)
- `Dockerfile` (add requirements.txt)
- `packaging/debian/control` (add Depends: python3-yaml)
- `packaging/rpm/redoubt.spec` (add Requires: python3-pyyaml)

---

### P0.3: Add Multi-Version Python Testing

**Problem:**
Only tests on Python 3.11 (Ubuntu 22.04 default). Claims to support "Python 3.10+" but never tests 3.10, 3.12, or 3.13.

**Impact:**
- Risk: May not work on Python 3.10 (breaking users who can't upgrade)
- Risk: May not work on Python 3.12+ (new releases, deprecated features)
- Risk: Version constraint in pyproject.toml may be incorrect

**Solution:**
1. Create Python version matrix for Phase 2 tests
2. Test on Python 3.10, 3.11, 3.12, 3.13
3. Use deadsnakes PPA for Ubuntu to get multiple Python versions
4. Update CI to test all versions

**Success Criteria:**
- [ ] PyPI Phase 2 tests run on Python 3.10, 3.11, 3.12, 3.13
- [ ] All tests pass on all versions
- [ ] pyproject.toml `requires-python` field validated
- [ ] CI matrix includes all versions

**Estimated Effort:** 2-3 days

**Dependencies:** None

**Implementation Notes:**
```bash
# In test-test-pypi-vm.sh
for PYTHON_VERSION in 3.10 3.11 3.12 3.13; do
  multipass launch -n test-pypi-py${PYTHON_VERSION} ubuntu:22.04
  multipass exec test-pypi-py${PYTHON_VERSION} -- sudo add-apt-repository ppa:deadsnakes/ppa
  multipass exec test-pypi-py${PYTHON_VERSION} -- sudo apt install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-venv
  multipass exec test-pypi-py${PYTHON_VERSION} -- python${PYTHON_VERSION} -m pip install --index-url https://test.pypi.org/simple/ demo-secure-cli
  multipass exec test-pypi-py${PYTHON_VERSION} -- demo_cli --version
done
```

**Files to Modify:**
- `scripts/phase2-testing/test-test-pypi-vm.sh`
- `.github/workflows/coverage.yml` (add matrix)
- `.github/workflows/integration-tests.yml` (add matrix)
- `docs/distribution/PLATFORM-SUPPORT.md`

---

### P0.4: Fix Windows Testing Automation

**Problem:**
Scoop, Chocolatey, WinGet have no automated VM testing. Scoop setup is automated but VM testing is manual. This is 3/17 platforms (18%) with no automated validation.

**Impact:**
- Risk: Windows packages may not work at all
- Risk: PowerShell scripts may have bugs
- Risk: Manual testing is slow and error-prone

**Solution:**
1. Evaluate Windows VM solutions (Hyper-V, VirtualBox, AWS EC2 Windows)
2. Implement automated Scoop testing with Windows VM
3. Implement automated Chocolatey testing with Windows VM
4. Implement automated WinGet testing with Windows VM
5. Add to Phase 2 comprehensive test suite

**Success Criteria:**
- [ ] Scoop Phase 2 VM test fully automated
- [ ] Chocolatey Phase 2 VM test implemented and automated
- [ ] WinGet Phase 2 VM test implemented and automated
- [ ] All three run in `comprehensive-vm-tests.sh`
- [ ] CI includes Windows testing (GitHub Actions windows-latest)

**Estimated Effort:** 5-7 days (Windows environment setup is complex)

**Dependencies:** Access to Windows VM platform (Hyper-V on Windows host, or cloud VM)

**Implementation Notes:**
```powershell
# Approach 1: GitHub Actions (fastest)
# .github/workflows/windows-testing.yml
jobs:
  test-windows:
    runs-on: windows-latest
    steps:
      - name: Test Scoop
        run: |
          iwr -useb get.scoop.sh | iex
          scoop bucket add OWNER https://github.com/OWNER/scoop-bucket
          scoop install redoubt
          redoubt --version

# Approach 2: Vagrant + VirtualBox (local testing)
# scripts/phase2-testing/test-windows-vm.sh
vagrant init gusztavvargadr/windows-11
vagrant up
vagrant ssh -c "powershell.exe -File test-scoop.ps1"
```

**Files to Create:**
- `scripts/phase2-testing/test-scoop-vm.ps1`
- `scripts/phase2-testing/test-chocolatey-vm.ps1`
- `scripts/phase2-testing/test-winget-vm.ps1`
- `.github/workflows/windows-testing.yml`

**Files to Modify:**
- `scripts/phase2-testing/comprehensive-vm-tests.sh` (add Windows tests)
- `docs/distribution/PLATFORM-SUPPORT.md`

---

## P0.5: Add Missing Platform Tests (CRITICAL - NEWLY DISCOVERED)

### P0.5a: AppImage Testing (ZERO COVERAGE)

**Problem:**
Complete packaging exists (`packaging/appimage/`) but **ZERO tests**. This is a complete blind spot.

**Impact:**
- Risk: AppImage may not work at all
- Risk: ~15% of Linux users affected (AppImage is popular for portable apps)
- Risk: Build script untested

**Solution:**
1. Add Phase 1 test: Local build and execution
2. Add Phase 2 test: Test on multiple distros in VMs

**Success Criteria:**
- [ ] Phase 1 test builds AppImage and verifies execution
- [ ] Phase 2 test runs AppImage on Ubuntu, Fedora, Debian VMs
- [ ] AppImage passes all verification checks

**Estimated Effort:** 1-2 days

**Files to Create:**
- `scripts/phase1-testing/appimage-local-build.sh`
- `scripts/phase2-testing/test-appimage-vm.sh`

---

### P0.5b: AUR Testing (ZERO COVERAGE)

**Problem:**
Complete PKGBUILD exists (`packaging/aur/`) but **ZERO tests**. Arch Linux users have no verification.

**Impact:**
- Risk: PKGBUILD may not work at all
- Risk: ~10% of Linux users affected (Arch is influential community)
- Risk: AUR submission will fail

**Solution:**
1. Add Phase 1 test: Docker-based makepkg build
2. Add Phase 2 test: Arch Linux VM installation

**Success Criteria:**
- [ ] Phase 1 test builds package with makepkg
- [ ] Phase 2 test installs on Arch Linux VM
- [ ] Package passes namcap validation

**Estimated Effort:** 1-2 days

**Files to Create:**
- `scripts/phase1-testing/aur-local-build.sh`
- `scripts/phase2-testing/test-aur-vm.sh`

---

### P0.5c: Nix Phase 1 Testing (ZERO COVERAGE)

**Problem:**
Complete `flake.nix` exists but never tested. Nix users have no verification.

**Impact:**
- Risk: Flake may not build at all
- Risk: Growing Nix community (~3% of Linux users)

**Solution:**
1. Add Phase 1 test: Local `nix build` test
2. Defer Phase 2 (Cachix) to P2

**Success Criteria:**
- [ ] Phase 1 test builds with `nix build`
- [ ] Phase 1 test runs `nix run`
- [ ] Flake passes `nix flake check`

**Estimated Effort:** 0.5-1 day

**Files to Create:**
- `scripts/phase1-testing/nix-local-build.sh`

---

## P1: High Priorities (Should Fix Before GA)

### P1.1: Add Flatpak Phase 2 Testing

**Problem:**
Flatpak has Phase 1 testing but no Phase 2 (real Flathub testing).

**Impact:**
- Risk: May not work on Flathub (actual distribution platform)
- Risk: ~30% of Linux desktop users use Flatpak

**Solution:**
Add Phase 2 testing with Flathub Beta repository

**Success Criteria:**
- [ ] Phase 2 test publishes to Flathub Beta
- [ ] Phase 2 test installs from Flathub Beta on VM
- [ ] Flatpak passes Flathub validation

**Estimated Effort:** 2-3 days

**Files to Create:**
- `scripts/phase2-testing/setup-flathub-beta.sh`
- `scripts/phase2-testing/test-flathub-beta-vm.sh`

---

### P1.2: Improve PyPI Phase 1 Simulator

**Problem:**
Uses basic `python3 -m http.server` instead of proper PyPI-compliant registry.

**Impact:**
- Doesn't test PEP 503 compliance
- Doesn't test dependency resolution
- Doesn't test complex scenarios (extras, markers)

**Solution:**
Replace with devpi (industry-standard private PyPI server)

**Success Criteria:**
- [ ] Phase 1 uses devpi instead of http.server
- [ ] Tests dependency resolution from upstream PyPI
- [ ] Tests extras and markers

**Estimated Effort:** 0.5-1 day

**Files to Modify:**
- `scripts/phase1-testing/pip-test-index.sh` → `pip-devpi-local.sh`

---

### P1.3: Add GitHub Packages for npm/RubyGems Phase 2

**Problem:**
npm and RubyGems only have Phase 1 local simulation, no real registry testing.

**Impact:**
- Assumption-based testing for 2 major platforms
- GitHub Packages supports both formats (real infrastructure available)

**Solution:**
Use GitHub Packages as Phase 2 real registry for npm and RubyGems

**Success Criteria:**
- [ ] npm Phase 2 publishes to GitHub Packages
- [ ] RubyGems Phase 2 publishes to GitHub Packages
- [ ] Both install from GitHub Packages in VMs

**Estimated Effort:** 2-3 days

**Files to Create:**
- `scripts/phase2-testing/setup-npm-github-packages.sh`
- `scripts/phase2-testing/test-npm-github-packages-vm.sh`
- `scripts/phase2-testing/setup-rubygems-github-packages.sh`
- `scripts/phase2-testing/test-rubygems-github-packages-vm.sh`

---

### P1.4: Add Multi-Distro Linux Testing

**Problem:**
Only tests Ubuntu 22.04 (APT) and Fedora 40 (RPM). Claims to support "Debian, Ubuntu, RHEL, CentOS" but never tests them.

**Impact:**
- Risk: May not work on Ubuntu 20.04 (still widely used)
- Risk: May not work on Debian 11/12
- Risk: May not work on RHEL 8/9 (enterprise standard)
- Risk: Package dependencies may differ across distros

**Solution:**
1. Add APT testing for Ubuntu 20.04, 22.04, 24.04
2. Add APT testing for Debian 11, 12
3. Add RPM testing for RHEL 8, 9 (via Rocky/Alma Linux)
4. Add RPM testing for CentOS Stream
5. Create distro matrix for CI

**Success Criteria:**
- [ ] APT tests pass on Ubuntu 20.04, 22.04, 24.04
- [ ] APT tests pass on Debian 11, 12
- [ ] RPM tests pass on Rocky Linux 8, 9
- [ ] RPM tests pass on Fedora 40
- [ ] CI matrix includes all distros

**Estimated Effort:** 3-4 days

**Dependencies:** P0.1 (GPG signatures) should be done first

**Implementation Notes:**
```bash
# Matrix approach in test-apt-repo-vm.sh
for DISTRO in ubuntu:20.04 ubuntu:22.04 ubuntu:24.04 debian:11 debian:12; do
  multipass launch -n test-apt-${DISTRO//:/} ${DISTRO}
  # ... run tests
done

# Matrix approach for RPM
for DISTRO in rockylinux:8 rockylinux:9 fedora:40; do
  multipass launch -n test-rpm-${DISTRO//:/} ${DISTRO}
  # ... run tests
done
```

**Files to Modify:**
- `scripts/phase2-testing/test-apt-repo-vm.sh`
- `scripts/phase2-testing/test-rpm-repo-vm.sh`
- `.github/workflows/integration-tests.yml`
- `docs/distribution/PLATFORM-SUPPORT.md`

---

### P1.5: Add Architecture Testing (ARM64)

**Problem:**
Only tests x86_64. Many production environments use ARM64 (AWS Graviton, Raspberry Pi, Apple Silicon).

**Impact:**
- Risk: Docker images may not work on ARM64
- Risk: Snap packages may not work on ARM64
- Risk: .pyz may have platform-specific dependencies

**Solution:**
1. Build multi-arch Docker images (amd64, arm64)
2. Test Docker on ARM64 VM or emulation
3. Test Snap on ARM64 VM
4. Verify .pyz on ARM64 (should work, but verify)
5. Update CI to build/test multi-arch

**Success Criteria:**
- [ ] Docker Phase 2 tests build and test amd64 + arm64 images
- [ ] Snap Phase 2 tests confirm ARM64 compatibility
- [ ] .pyz verified on ARM64 VM
- [ ] CI builds multi-arch Docker images

**Estimated Effort:** 3-4 days

**Dependencies:** None (can run in parallel with other work)

**Implementation Notes:**
```bash
# Docker multi-arch build
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64 -t ghcr.io/OWNER/redoubt:test .

# QEMU emulation for ARM64 testing
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
multipass launch -n test-arm64 ubuntu:22.04
multipass exec test-arm64 -- dpkg --print-architecture  # Should be arm64
```

**Files to Modify:**
- `Dockerfile` (use multi-arch base images)
- `scripts/phase2-testing/setup-docker-registry.sh`
- `scripts/phase2-testing/test-docker-registry-vm.sh`
- `.github/workflows/release.yml` (add multi-arch build)
- `docs/distribution/PLATFORM-SUPPORT.md`

---

### P1.6: Add macOS Native Homebrew Testing

**Problem:**
Phase 2 only tests Homebrew on Linux. macOS is the primary Homebrew platform and may have different behavior.

**Impact:**
- Risk: Formula may not work on macOS (different paths, dependencies)
- Risk: Code signing requirements on macOS
- Risk: macOS-specific security restrictions (Gatekeeper)

**Solution:**
1. Add macOS CI runner (GitHub Actions macos-latest)
2. Test Homebrew installation on macOS
3. Test formula compatibility with macOS paths
4. Verify code signing requirements

**Success Criteria:**
- [ ] Homebrew Phase 2 test runs on macOS (in addition to Linux)
- [ ] Formula installs successfully on macOS 13, 14
- [ ] Binary runs without Gatekeeper warnings
- [ ] CI includes macOS testing

**Estimated Effort:** 2-3 days

**Dependencies:** None

**Implementation Notes:**
```yaml
# .github/workflows/homebrew-testing.yml
jobs:
  test-homebrew-macos:
    runs-on: macos-latest
    steps:
      - name: Install from tap
        run: |
          brew tap OWNER/homebrew-tap
          brew install redoubt
          redoubt --version
```

**Files to Create:**
- `.github/workflows/homebrew-testing.yml`

**Files to Modify:**
- `scripts/phase2-testing/test-homebrew-tap-vm.sh` (add macOS variant)
- `packaging/homebrew-tap/Formula/provenance-demo.rb`
- `docs/distribution/PLATFORM-SUPPORT.md`

---

### P1.7: Add Update/Upgrade Testing

**Problem:**
No testing of version upgrades. We never test if users can upgrade from v1.0.0 to v1.1.0.

**Impact:**
- Risk: Breaking changes may break existing installations
- Risk: Migration scripts may be needed but not tested
- Risk: Config file compatibility issues
- Risk: Data loss on upgrade

**Solution:**
1. Create upgrade test scenarios (v1.0.0 → v1.1.0)
2. Test in-place upgrades for all major platforms
3. Test rollback scenarios
4. Test config file migration
5. Test data preservation

**Success Criteria:**
- [ ] PyPI: Test `pip install --upgrade`
- [ ] APT: Test `apt upgrade`
- [ ] RPM: Test `dnf upgrade`
- [ ] Homebrew: Test `brew upgrade`
- [ ] Docker: Test pulling new tag
- [ ] Snap: Test snap refresh
- [ ] All platforms preserve user data/config

**Estimated Effort:** 4-5 days

**Dependencies:** Requires at least 2 versions to test upgrade path

**Implementation Notes:**
```bash
# Approach: Two-phase test
# Phase A: Install v1.0.0
pip install demo-secure-cli==1.0.0
demo_cli config set key=value

# Phase B: Upgrade to v1.1.0
pip install --upgrade demo-secure-cli==1.1.0
demo_cli config get key  # Should still be 'value'
demo_cli --version  # Should be 1.1.0
```

**Files to Create:**
- `scripts/phase2-testing/test-upgrade-pypi.sh`
- `scripts/phase2-testing/test-upgrade-apt.sh`
- `scripts/phase2-testing/test-upgrade-rpm.sh`
- `scripts/phase2-testing/test-upgrade-homebrew.sh`
- `docs/testing/UPGRADE-TESTING.md`

---

## P2: Medium Priorities (Post-GA)

### P2.1: Add Phase 2 Testing for npm, Cargo, RubyGems, Conda

**Problem:**
10/17 platforms only have Phase 1 local simulation. No real registry testing.

**Impact:**
- Risk: May claim to support these platforms but they're undertested
- Missing validation of real registry integration

**Solution:**
1. Implement Phase 2 testing for npm (publish to npm registry test instance or private registry)
2. Implement Phase 2 testing for Cargo (crates.io or private registry)
3. Implement Phase 2 testing for RubyGems (rubygems.org or private)
4. Implement Phase 2 testing for Conda (anaconda.org test or private channel)

**Success Criteria:**
- [ ] npm Phase 2 test publishes to registry and installs in VM
- [ ] Cargo Phase 2 test publishes to registry and installs in VM
- [ ] RubyGems Phase 2 test publishes to registry and installs in VM
- [ ] Conda Phase 2 test publishes to channel and installs in VM

**Estimated Effort:** 6-8 days (2 days per platform)

**Dependencies:** None (can defer to post-GA)

**Implementation Notes:**
```bash
# npm approach (using npm registry or GitHub Packages)
npm publish --registry=https://npm.pkg.github.com/

# Cargo approach (using private registry via crates.io-index fork)
cargo publish --registry=private

# RubyGems approach (using rubygems.org or gemfury)
gem push --host https://rubygems.org/

# Conda approach (using anaconda.org test)
anaconda upload dist/package.tar.bz2
```

**Files to Create:**
- `scripts/phase2-testing/setup-npm-registry.sh`
- `scripts/phase2-testing/test-npm-registry-vm.sh`
- `scripts/phase2-testing/setup-cargo-registry.sh`
- `scripts/phase2-testing/test-cargo-registry-vm.sh`
- And similar for RubyGems, Conda

---

### P2.2: Add Offline/Air-Gapped Installation Testing

**Problem:**
All tests assume Internet connectivity. Enterprise users often need offline installation.

**Impact:**
- Risk: May not support air-gapped deployments
- Missing: Vendor dependency bundles
- Missing: Local mirror setup instructions

**Solution:**
1. Create vendored dependency bundles
2. Test installation from local mirror (no Internet)
3. Document offline installation process
4. Test with network disabled in VM

**Success Criteria:**
- [ ] PyPI offline installation works (wheelhouse)
- [ ] APT offline installation works (local repo mirror)
- [ ] Docker offline installation works (saved image tarball)
- [ ] Documentation for offline installation

**Estimated Effort:** 3-4 days

**Dependencies:** None

**Implementation Notes:**
```bash
# PyPI offline approach
pip download -d wheelhouse demo-secure-cli
# On offline machine:
pip install --no-index --find-links=wheelhouse demo-secure-cli

# Docker offline approach
docker save ghcr.io/OWNER/redoubt:latest -o redoubt.tar
# On offline machine:
docker load -i redoubt.tar
```

**Files to Create:**
- `scripts/phase2-testing/test-offline-pypi.sh`
- `scripts/phase2-testing/test-offline-apt.sh`
- `scripts/phase2-testing/test-offline-docker.sh`
- `docs/distribution/OFFLINE-INSTALLATION.md`

---

### P2.3: Add Security Scanning Integration

**Problem:**
No automated security scanning of containers or packages.

**Impact:**
- Missing vulnerability detection
- No SBOM validation
- No supply chain verification beyond what's in release workflow

**Solution:**
1. Add Trivy scanning for Docker images
2. Add Grype scanning for packages
3. Add SBOM generation validation
4. Add dependency vulnerability scanning
5. Integrate into CI

**Success Criteria:**
- [ ] Docker images scanned with Trivy in CI
- [ ] Packages scanned with Grype in CI
- [ ] SBOM generated and validated (CycloneDX)
- [ ] Vulnerability reports published
- [ ] CI fails on HIGH/CRITICAL vulnerabilities

**Estimated Effort:** 2-3 days

**Dependencies:** None

**Implementation Notes:**
```yaml
# .github/workflows/security-scanning.yml
- name: Scan Docker image
  run: |
    docker pull aquasec/trivy:latest
    trivy image --severity HIGH,CRITICAL ghcr.io/OWNER/redoubt:latest

- name: Scan package dependencies
  run: |
    curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh
    grype sbom:sbom.cdx.json
```

**Files to Create:**
- `.github/workflows/security-scanning.yml`
- `docs/security/SECURITY-SCANNING.md`

---

### P2.4: Add Performance Benchmarking

**Problem:**
No validation of binary size, startup time, or memory usage.

**Impact:**
- Risk: Performance regressions undetected
- Missing baseline metrics

**Solution:**
1. Add binary size validation (<10MB)
2. Add startup time benchmarking (<100ms)
3. Add memory usage profiling (<50MB)
4. Track metrics over time

**Success Criteria:**
- [ ] CI fails if .pyz >10MB
- [ ] CI fails if startup time >100ms
- [ ] CI fails if memory usage >50MB
- [ ] Metrics tracked in README badge

**Estimated Effort:** 2-3 days

**Dependencies:** None

**Implementation Notes:**
```bash
# Size check
SIZE=$(stat -f%z dist/client.pyz)
if [ $SIZE -gt 10485760 ]; then
  echo "Binary too large: $SIZE bytes"
  exit 1
fi

# Startup time
time ./dist/client.pyz --version

# Memory usage
/usr/bin/time -v ./dist/client.pyz hello 2>&1 | grep "Maximum resident set size"
```

**Files to Create:**
- `scripts/phase2-testing/test-performance.sh`
- `docs/testing/PERFORMANCE-TESTING.md`

---

## P3: Low Priorities (Future Work)

### P3.1: Add i18n/Locale Testing

**Problem:**
No testing of non-English locales or UTF-8 support.

**Impact:**
- Risk: May not work correctly with non-ASCII characters
- Missing international user support

**Solution:**
1. Test with various locales (ja_JP, zh_CN, de_DE)
2. Test UTF-8 input/output
3. Test locale-specific behavior

**Estimated Effort:** 2-3 days

---

### P3.2: Add Central Registry Publishing (Phase 3 Automation)

**Problem:**
Phase 2 uses test/draft registries. No automation for production publishing.

**Impact:**
- Manual Phase 3 publishing is slow and error-prone
- No validation of central registry submission process

**Solution:**
1. Automate Homebrew homebrew-core PR creation
2. Automate Docker Hub publishing
3. Automate PyPI production publishing
4. Automate Snap stable channel release

**Estimated Effort:** 4-6 days

---

### P3.3: Add Telemetry/Analytics Testing

**Problem:**
If telemetry is added, no testing of analytics collection.

**Estimated Effort:** 2-3 days

---

## Implementation Roadmap

### Sprint 1 (Week 1-2): Critical Blockers
- **P0.1:** GPG Signatures (2-3 days)
- **P0.2:** Real Dependencies (1-2 days)
- **P0.3:** Multi-Version Python (2-3 days)
- **P0.4:** Windows Automation (5-7 days)
- **P0.5a:** AppImage Testing (1-2 days) - **NEWLY ADDED**
- **P0.5b:** AUR Testing (1-2 days) - **NEWLY ADDED**
- **P0.5c:** Nix Phase 1 Testing (0.5-1 day) - **NEWLY ADDED**

**Total:** ~16-20 days (4 weeks with 1 person, or 2 weeks with 2 people) - **INCREASED from original 12 days**

### Sprint 2 (Week 3-5): High Priority Improvements
- **P1.1:** Flatpak Phase 2 (2-3 days) - **NEWLY ADDED**
- **P1.2:** Improve PyPI Simulator (0.5-1 day) - **NEWLY ADDED**
- **P1.3:** GitHub Packages npm/RubyGems (2-3 days) - **NEWLY ADDED**
- **P1.4:** Multi-Distro Linux (3-4 days)
- **P1.5:** ARM64 Architecture (3-4 days)
- **P1.6:** macOS Homebrew (2-3 days)
- **P1.7:** Update Testing (4-5 days)

**Total:** ~18-22 days (4-5 weeks) - **INCREASED from original 13 days**

### Sprint 3 (Week 6-8): Medium Priority (Post-GA)
- **P2.1:** Cargo/Conda/Helm Phase 2 (6-8 days)
- **P2.2:** Nix Phase 2 with Cachix (2-3 days) - **NEWLY ADDED**
- **P2.3:** Improve Go/Terraform Phase 1 (2-3 days) - **NEWLY ADDED**
- **P2.4:** Offline Installation (3-4 days)
- **P2.5:** Security Scanning (2-3 days)
- **P2.6:** Performance Benchmarking (2-3 days)

**Total:** ~19-24 days (4-5 weeks) - **INCREASED from original 14 days**

---

## Success Metrics

### Definition of "Production Ready"

A platform is considered production-ready when:

1. ✅ Phase 1 local testing passes
2. ✅ Phase 2 VM testing passes with real registry
3. ✅ GPG/code signing implemented and tested
4. ✅ Real dependencies resolve correctly
5. ✅ Multi-version testing passes (where applicable)
6. ✅ Multi-distro testing passes (where applicable)
7. ✅ Documentation complete
8. ✅ At least one manual Phase 3 deployment successful

### Current Production Readiness Score (REVISED - 21 Platforms)

| Platform | Phase 1 | Phase 2 | GPG | Deps | Multi-Ver | Multi-Distro | Docs | Phase 3 | Score |
|----------|---------|---------|-----|------|-----------|--------------|------|---------|-------|
| PyPI     | ⚠️ | ✅ | N/A | ❌ | ❌ | N/A | ✅ | ❌ | 2.5/6 (42%) |
| Homebrew | ✅ | ✅ | N/A | ❌ | N/A | ⚠️ | ✅ | ❌ | 3/6 (50%) |
| Docker   | ✅ | ✅ | N/A | ❌ | N/A | ⚠️ | ✅ | ❌ | 3/6 (50%) |
| Snap     | ⚠️ | ✅ | N/A | N/A | N/A | ⚠️ | ✅ | ❌ | 2.5/5 (50%) |
| APT      | ✅ | ✅ | ❌ | ❌ | N/A | ❌ | ✅ | ❌ | 3/7 (43%) |
| RPM      | ✅ | ✅ | ❌ | ❌ | N/A | ❌ | ✅ | ❌ | 3/7 (43%) |
| **Flatpak** | ✅ | ❌ | N/A | N/A | N/A | ⚠️ | ✅ | ❌ | 2/5 (40%) |
| **AppImage** | ❌ | ❌ | N/A | N/A | N/A | ❌ | ✅ | ❌ | 1/5 (20%) |
| **AUR** | ❌ | ❌ | N/A | ❌ | N/A | N/A | ✅ | ❌ | 1/5 (20%) |
| **Nix** | ❌ | ❌ | N/A | ❌ | N/A | N/A | ✅ | ❌ | 1/5 (20%) |
| npm      | ✅ | ❌ | N/A | ❌ | N/A | N/A | ✅ | ❌ | 2/5 (40%) |
| Cargo    | ✅ | ❌ | N/A | ❌ | N/A | N/A | ✅ | ❌ | 2/5 (40%) |
| Scoop    | ⚠️ | ⚠️ | N/A | ❌ | N/A | N/A | ✅ | ❌ | 2/5 (40%) |
| Chocolatey | ⚠️ | ❌ | N/A | ❌ | N/A | N/A | ✅ | ❌ | 1.5/5 (30%) |
| WinGet   | ⚠️ | ❌ | N/A | ❌ | N/A | N/A | ✅ | ❌ | 1.5/5 (30%) |

**Legend:**
- ✅ Complete
- ⚠️ Partial (suboptimal simulator or incomplete)
- ❌ Missing
- N/A Not applicable
- **Bold**: Newly identified in reassessment

**Average Production Readiness:** ~38% (DECREASED from initial 46% due to more platforms discovered)

**Note:** PyPI Phase 1 downgraded to ⚠️ due to suboptimal simulator (http.server vs devpi)

**Target After Sprint 1 (P0 Complete):** 65% (REVISED - more work identified)
**Target After Sprint 2 (P0+P1 Complete):** 85% (REVISED)
**Target for GA Release:** 95%+

---

## Risk Assessment

### High-Risk Items (Could Block GA)

1. **GPG Implementation Complexity** (P0.1)
   - Risk: GPG key management is complex, may take longer than estimated
   - Mitigation: Start with simple approach, iterate

2. **Windows VM Availability** (P0.4)
   - Risk: May not have access to Windows VMs
   - Mitigation: Use GitHub Actions windows-latest as primary approach

3. **Multi-Version Testing Flakiness** (P0.3)
   - Risk: Different Python versions may expose bugs
   - Mitigation: Start with 3.10 and 3.12, expand gradually

### Medium-Risk Items

1. **ARM64 Hardware Access** (P1.2)
   - Risk: May need ARM64 hardware for testing
   - Mitigation: Use QEMU emulation as fallback

2. **Upgrade Testing Requires Multiple Versions** (P1.4)
   - Risk: Can't test upgrades until we have 2+ releases
   - Mitigation: Create fake v1.0.0 and v1.1.0 for testing

---

## Decision Log

### 2025-10-25: Plan Created
- Prioritized P0 items as blockers for GA release
- Decided GPG signatures are critical (P0.1)
- Decided Windows automation is critical (P0.4)
- Deferred Phase 2 for npm/Cargo/etc to P2 (post-GA acceptable)

---

## Appendix: Platform-Specific Notes

### APT/RPM: GPG Signing Differences

**APT:**
- Signs repository metadata (Release, InRelease)
- Users import public key via `apt-key` or `/etc/apt/trusted.gpg.d/`
- Verification is per-repository, not per-package

**RPM:**
- Signs individual .rpm files
- Users import public key via `rpm --import`
- Verification is per-package

### Windows: Code Signing Requirements

**Scoop:**
- Does not require code signing
- Verifies SHA256 from manifest

**Chocolatey:**
- Recommends code signing for trusted packages
- Requires code signing for moderation approval

**WinGet:**
- Does not require code signing
- Verifies SHA256 from manifest

**Recommendation:** Defer code signing to Phase 3, focus on SHA256 verification for Phase 2.

---

## Next Steps

1. Review this plan with stakeholders
2. Create GitHub issues for each P0 item
3. Assign Sprint 1 work
4. Begin implementation of P0.1 (GPG signatures)
5. Update project roadmap with timelines

---

## References

- **[TESTING-REASSESSMENT.md](./TESTING-REASSESSMENT.md)** - Critical findings from reassessment (READ THIS FIRST)
- [Testing Infrastructure Analysis](./TESTING-APPROACHES-COMPARISON.md)
- [Testing Strategy](./TESTING-STRATEGY.md)
- [Platform Support Matrix](../distribution/PLATFORM-SUPPORT.md)
- [Security Checklist](../security/COMPLETE-SECURITY-CHECKLIST.md)

---

## Revision History

### 2025-10-25 (Revision 2)
- **CRITICAL UPDATE**: Discovered 4 missed platforms after reassessment
- Added P0.5a/b/c for AppImage, AUR, Nix Phase 1 testing
- Added P1.1/2/3 for Flatpak Phase 2, PyPI simulator improvement, GitHub Packages
- Revised effort estimates: Sprint 1 increased from 12 days to 16-20 days
- Revised production readiness: 46% → 38% (more platforms, more gaps)
- See [TESTING-REASSESSMENT.md](./TESTING-REASSESSMENT.md) for full details

### 2025-10-25 (Revision 1)
- Initial version created
