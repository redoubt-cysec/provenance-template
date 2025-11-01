# Platform Support Status

**Last Updated:** 2025-11-01

This document provides complete transparency about platform support status, testing coverage, and production readiness.

## Summary

- **✅ Fully Ready (Production):** 5 platforms
- **🟡 Configuration Ready (Testing Pending):** 8 platforms
- **⚪ Template/Planned:** 6 platforms
- **Total Documented:** 19 platforms

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Fully implemented and tested |
| 🟡 | Configuration exists, testing incomplete |
| ⚪ | Template only or planned |
| ❌ | Not implemented |

## Detailed Platform Status

### Core Python Distribution

| Platform | Config | Phase 1 Tests | Phase 2 Tests | Workflow | Production | Notes |
|----------|--------|---------------|---------------|----------|------------|-------|
| **PyPI (pip)** | ✅ | ✅ | ✅ | ✅ | ✅ | `pyproject.toml` + pypi-publish.yml |
| **pipx** | ✅ | ✅ | ✅ | ✅ | ✅ | Same as PyPI, tested in integration |
| **Direct .pyz** | ✅ | ✅ | ✅ | ✅ | ✅ | Primary distribution, fully tested |
| **GitHub Releases** | ✅ | ✅ | ✅ | ✅ | ✅ | secure-release.yml workflow |
| **Conda** | ⚪ | ❌ | ❌ | ❌ | ⚪ | Planned - needs meta.yaml |

**Config Files:** [pyproject.toml](../../pyproject.toml), [build_pyz.sh](../../scripts/build_pyz.sh)
**Tests:** test_distribution_integration.py, test_cli.py
**Workflows:** [pypi-publish.yml](../../.github/workflows/pypi-publish.yml), [secure-release.yml](../../.github/workflows/secure-release.yml)

---

### Linux Package Managers

| Platform | Config | Phase 1 Tests | Phase 2 Tests | Workflow | Production | Notes |
|----------|--------|---------------|---------------|----------|------------|-------|
| **Homebrew (Linux)** | ✅ | ✅ | ✅ | ✅ | ✅ | Formula + tap workflow |
| **Snap** | ✅ | ✅ | ✅ | ✅ | ✅ | snapcraft.yaml, VM tested |
| **Flatpak** | ✅ | ✅ | 🟡 | ✅ | 🟡 | Manifest exists, Flathub Beta in progress |
| **APT (Debian/Ubuntu)** | ✅ | ✅ | 🟡 | ❌ | 🟡 | debian/ control files, needs repo workflow |
| **RPM (Fedora/RHEL)** | ✅ | ✅ | 🟡 | ❌ | 🟡 | .spec file, needs repo workflow |
| **AUR (Arch Linux)** | ✅ | ✅ | 🟡 | ❌ | 🟡 | PKGBUILD exists, needs publish workflow |
| **AppImage** | ✅ | ✅ | 🟡 | ❌ | 🟡 | AppImageBuilder.yml, needs workflow |
| **Nix/NixOS** | ✅ | ✅ | 🟡 | ✅ | 🟡 | flake.nix, cachix workflow exists |

**Config Files:**
- [packaging/homebrew-tap/](../../packaging/homebrew-tap/)
- [packaging/snap/snapcraft.yaml](../../packaging/snap/snapcraft.yaml)
- [packaging/flatpak/](../../packaging/flatpak/)
- [packaging/debian/](../../packaging/debian/)
- [packaging/rpm/redoubt.spec](../../packaging/rpm/redoubt.spec)
- [packaging/aur/PKGBUILD](../../packaging/aur/PKGBUILD)
- [packaging/appimage/](../../packaging/appimage/)
- [flake.nix](../../flake.nix)

**Tests:** test_platform_configurations.py (48 tests), test_distribution_integration.py
**Workflows:**
- [homebrew-tap.yml](../../.github/workflows/homebrew-tap.yml)
- [snap-publish.yml](../../.github/workflows/snap-publish.yml)
- [flatpak-beta.yml](../../.github/workflows/flatpak-beta.yml)
- [nix-cachix.yml](../../.github/workflows/nix-cachix.yml)

---

### macOS

| Platform | Config | Phase 1 Tests | Phase 2 Tests | Workflow | Production | Notes |
|----------|--------|---------------|---------------|----------|------------|-------|
| **Homebrew (macOS)** | ✅ | ✅ | ✅ | ✅ | ✅ | Same Formula as Linux, VM tested |
| **Nix (macOS)** | ✅ | ✅ | 🟡 | ✅ | 🟡 | Same flake.nix as Linux |
| **Direct .pyz** | ✅ | ✅ | ✅ | ✅ | ✅ | Works on macOS |

**Config Files:** Same as Linux sections above
**Tests:** test_distribution_integration.py (macOS VM fixture)
**Workflows:** [homebrew-macos.yml](../../.github/workflows/homebrew-macos.yml)

---

### Windows

| Platform | Config | Phase 1 Tests | Phase 2 Tests | Workflow | Production | Notes |
|----------|--------|---------------|---------------|----------|------------|-------|
| **Chocolatey** | ✅ | ✅ | 🟡 | ✅ | 🟡 | .nuspec + build_chocolatey.ps1 |
| **WinGet** | ✅ | ✅ | 🟡 | ✅ | 🟡 | Manifest + build_winget.ps1 |
| **Scoop** | ✅ | ✅ | 🟡 | ❌ | 🟡 | JSON manifest, needs bucket workflow |
| **Direct .pyz** | ✅ | ✅ | ✅ | ✅ | ✅ | Works on Windows |

**Config Files:**
- [packaging/chocolatey/redoubt.nuspec](../../packaging/chocolatey/redoubt.nuspec)
- [packaging/winget/manifests/](../../packaging/winget/manifests/)
- [packaging/scoop/provenance-demo.json](../../packaging/scoop/provenance-demo.json)
- [scripts/build_chocolatey.ps1](../../scripts/build_chocolatey.ps1)
- [scripts/build_winget.ps1](../../scripts/build_winget.ps1)

**Tests:** test_platform_configurations.py (validation tests)
**Workflows:** [secure-release.yml](../../.github/workflows/secure-release.yml) (Chocolatey + Winget)

---

### Containers

| Platform | Config | Phase 1 Tests | Phase 2 Tests | Workflow | Production | Notes |
|----------|--------|---------------|---------------|----------|------------|-------|
| **Docker** | ✅ | ✅ | ✅ | ✅ | ✅ | Dockerfile + docker-multiarch.yml |
| **OCI/GHCR** | ✅ | ✅ | ✅ | ✅ | ✅ | Same as Docker, published to ghcr.io |

**Config Files:** [Dockerfile](../../Dockerfile)
**Tests:** test_platform_configurations.py (4 Docker tests)
**Workflows:** [docker-multiarch.yml](../../.github/workflows/docker-multiarch.yml)

---

### Other Ecosystems (Planned/Template Only)

| Platform | Status | Notes |
|----------|--------|-------|
| **npm** | ⚪ Planned | Would wrap .pyz for Node ecosystem |
| **Cargo (Rust)** | ⚪ Planned | Would wrap .pyz for Rust ecosystem |
| **RubyGems** | ⚪ Planned | Would wrap .pyz for Ruby ecosystem |
| **Go modules** | ⚪ Planned | Would wrap .pyz for Go ecosystem |
| **Helm charts** | ⚪ Planned | Would package Docker image |
| **Terraform modules** | ⚪ Planned | Would reference released artifacts |

**Status:** These are aspirational - no configuration files exist yet.

---

## Platform Readiness Criteria

### ✅ Production Ready
- Configuration files exist and are valid
- Phase 1 validation tests pass
- Phase 2 VM/integration tests pass
- Automated workflow exists
- Successfully published at least once
- Documentation complete

**Platforms meeting criteria:**
1. PyPI (pip)
2. pipx
3. Direct .pyz
4. GitHub Releases
5. Homebrew (macOS + Linux)
6. Snap
7. Docker/OCI

### 🟡 Configuration Ready
- Configuration files exist and are valid
- Phase 1 validation tests pass
- Phase 2 tests missing or incomplete
- Workflow may be missing or incomplete
- Not yet published to production

**Platforms meeting criteria:**
1. Flatpak (Flathub Beta in progress)
2. APT/Debian (needs repository setup)
3. RPM/Fedora (needs repository setup)
4. AUR/Arch (needs publish workflow)
5. AppImage (needs workflow)
6. Nix/NixOS (Cachix in progress)
7. Chocolatey (needs testing)
8. WinGet (needs testing)
9. Scoop (needs bucket workflow)

### ⚪ Planned/Template Only
- No configuration files
- No tests
- No workflow
- Listed as future possibility

**Platforms:** Conda, npm, Cargo, RubyGems, Go modules, Helm, Terraform

---

## Test Coverage Details

### Phase 1: Validation Tests (Fast)
**File:** [test_platform_configurations.py](../../tests/test_platform_configurations.py)
**Count:** 48 tests
**Runtime:** <5 seconds

Tests configuration file syntax and structure:
- ✅ Docker: 4 tests
- ✅ Scoop: 4 tests
- ✅ WinGet: 4 tests
- ✅ Debian: 4 tests
- ✅ RPM: 4 tests
- ✅ Flatpak: 6 tests
- ✅ AppImage: 4 tests
- ✅ Nix: 4 tests
- ✅ Chocolatey: 4 tests
- ✅ AUR: 4 tests
- ✅ GitHub Action: 4 tests
- ✅ Cross-platform consistency: 2 tests

### Phase 2: Integration Tests (Comprehensive)
**File:** [test_distribution_integration.py](../../tests/test_distribution_integration.py)
**Count:** 8 tests
**Runtime:** ~15-20 minutes

Tests actual installation and execution:
- ✅ Homebrew tap install (macOS VM)
- ✅ Snap install (Ubuntu VM)
- ✅ pip/wheel install (Ubuntu VM)
- ✅ pipx install (Ubuntu VM)
- ✅ Direct .pyz execution (Ubuntu VM)
- ✅ Python version compatibility (Ubuntu VM)
- ✅ End-to-end attestation verification (Ubuntu VM)
- ✅ Homebrew formula validation

**VM Fixtures:** Ubuntu 22.04, macOS (via GitHub Actions runner)

### Phase 3: Published Distribution Tests
**File:** [test_published_distributions.py](../../tests/test_published_distributions.py)
**Count:** 10 tests
**Runtime:** ~10-20 minutes

Tests real published packages work:
- ✅ GitHub release download
- ✅ Attestation verification
- ✅ Checksum verification
- ✅ (Optional) Homebrew tap install
- ✅ (Optional) PyPI install

---

## Workflow Automation

### Fully Automated
- **secure-release.yml**: Builds and publishes .pyz, Chocolatey, WinGet to GitHub Releases
- **homebrew-tap.yml**: Updates Homebrew formula in tap repository
- **snap-publish.yml**: Publishes to Snap Store
- **docker-multiarch.yml**: Builds and pushes Docker images
- **flatpak-beta.yml**: Publishes to Flathub Beta
- **pypi-publish.yml**: Publishes to PyPI
- **nix-cachix.yml**: Publishes to Cachix cache

### Manual/Incomplete
- **APT repository**: Needs setup and automation
- **RPM repository**: Needs setup and automation
- **AUR**: Needs publish workflow
- **AppImage**: Needs build and publish workflow
- **Scoop**: Needs bucket repository and workflow

---

## Roadmap to 100% Coverage

### Short Term (Complete existing platforms)
1. ✅ Add Harden-Runner to secure-release.yml (PR #59)
2. 🟡 Complete Flatpak Flathub Beta testing
3. 🟡 Complete Nix Cachix setup
4. 🟡 Add Phase 2 VM tests for Chocolatey
5. 🟡 Add Phase 2 VM tests for WinGet
6. 🟡 Add Phase 2 VM tests for Scoop

### Medium Term (Enable configured platforms)
7. 🟡 Create APT repository workflow
8. 🟡 Create RPM repository workflow
9. 🟡 Create AUR publish workflow
10. 🟡 Create AppImage build and publish workflow
11. 🟡 Create Scoop bucket repository and workflow

### Long Term (New platforms)
12. ⚪ Add Conda meta.yaml and workflow
13. ⚪ Evaluate npm wrapper (if demand exists)
14. ⚪ Evaluate other language ecosystem wrappers

---

## How to Read This Document

**When claiming platform support**, use these accurate statements:

### Accurate Claims ✅
- "Supports **7 production-ready platforms** with full testing"
- "Provides **configuration templates for 13+ platforms**"
- "Includes **automated workflows for 7 platforms**"
- "Has **Phase 1 validation tests for 13 platforms**"
- "Features **Phase 2 integration tests for 7 platforms**"

### Misleading Claims ❌
- ~~"Supports 18 platforms"~~ (conflates ready + configured + planned)
- ~~"All platforms include Phase 2 testing"~~ (only 7 have it)
- ~~"Tested across 18 platforms"~~ (only 7 fully tested)

---

## Contributing

To move a platform from 🟡 to ✅:

1. **Add Phase 2 VM tests** in test_distribution_integration.py
2. **Create or complete workflow** for automated publishing
3. **Test end-to-end** with real release
4. **Update documentation** with installation instructions
5. **Submit PR** updating this status document

See [CONTRIBUTING.md](../contributing/CONTRIBUTING.md) for details.

---

## Questions?

- **Why are some platforms 🟡 if config exists?** Configuration alone doesn't guarantee it works. We need integration testing and workflow automation.

- **Can I use 🟡 platforms now?** Yes! The configuration files work. You'll just need to build/publish manually until workflows are complete.

- **When will ⚪ platforms be implemented?** When there's demonstrated user demand and a maintainer to own the integration.

- **How do I request a new platform?** Open an issue with the platform name, your use case, and whether you can help test/maintain it.

---

**This document is the single source of truth for platform support status.**
All other documentation should link here for platform details.
