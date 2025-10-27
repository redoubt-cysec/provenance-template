# Testing Quick Reference

**Last Updated:** 2025-10-25

## Quick Command Map

### New Platform Tests (P0.5)

```bash
# AppImage
just test-appimage-p1        # Local build and test
just test-appimage-p2        # VM testing (Ubuntu, Debian, Fedora)

# AUR (Arch Linux)
just test-aur-p1             # Docker-based makepkg build
just test-aur-p2             # Arch Linux VM installation

# Nix
just test-nix-p1             # Local nix build and run
```

### Improved Simulators (P1)

```bash
# PyPI with devpi (better than http.server)
just test-pypi-devpi         # Full PyPI protocol, upstream mirroring

# Flatpak Beta
just test-flatpak-beta-setup # Build and prepare for Flathub Beta
just test-flatpak-beta-vm    # VM testing with Beta remote
```

### Multi-Architecture (P1.5)

```bash
# Docker multi-arch (amd64 + arm64)
just test-docker-multiarch IMG=ghcr.io/OWNER/redoubt:test
```

### Release Signing (P0.1)

```bash
# APT repository signing
GPG_KEY_NAME="Release Key" just sign-apt dist/deb-repo

# RPM package signing
GPG_KEY_NAME="Release Key" just sign-rpm dist/rpm
```

### Convenience Commands

```bash
# Run all new Phase 1 tests
just test-new-platforms-p1

# Run all Phase 1 tests
just test-phase1-all

# Run all Phase 2 VM tests
just test-phase2-all
```

## Test Coverage Matrix

| Platform | Phase 1 | Phase 2 | Just Command |
|----------|---------|---------|--------------|
| AppImage | ✅ | ✅ | `just test-appimage-p1/p2` |
| AUR | ✅ | ✅ | `just test-aur-p1/p2` |
| Nix | ✅ | 🚧 | `just test-nix-p1` |
| Flatpak | ✅ | 🚧 | `just test-flatpak-beta-*` |
| PyPI (devpi) | ✅ | ✅ | `just test-pypi-devpi` |
| Docker (multi-arch) | ✅ | ✅ | `just test-docker-multiarch` |

## Scripts Location Reference

### Phase 1 Tests (Local/Docker)
- `scripts/phase1-testing/appimage-local-build.sh`
- `scripts/phase1-testing/aur-local-build.sh`
- `scripts/phase1-testing/nix-local-build.sh`
- `scripts/phase1-testing/pip-devpi-local.sh`

### Phase 2 Tests (VM-Based)
- `scripts/phase2-testing/test-appimage-vm.sh`
- `scripts/phase2-testing/test-aur-vm.sh`
- `scripts/phase2-testing/setup-flathub-beta.sh`
- `scripts/phase2-testing/test-flathub-beta-vm.sh`
- `scripts/phase2-testing/test-docker-multiarch.sh`

### Release Signing
- `scripts/release/sign-apt-repo.sh`
- `scripts/release/sign-rpm.sh`

## CI Workflows

### Windows Testing
`.github/workflows/windows-testing.yml`
- Tests Scoop, Chocolatey, WinGet
- Validates manifests
- Runs on `windows-latest`

## Prerequisites

### For Local Testing
- **Docker**: Required for AUR, Flatpak, multi-arch tests
- **Nix**: Required for Nix tests (optional if not testing Nix)
- **multipass**: Required for Phase 2 VM tests
- **just**: Command runner (or use `bash scripts/...` directly)

### For Signing
- **GPG**: Required for APT/RPM signing
- Generate key: `gpg --gen-key`
- Export: `gpg --export --armor "Your Name" > key.asc`

## Troubleshooting

### "multipass not found"
```bash
# macOS
brew install multipass

# Linux
snap install multipass
```

### "Docker not available"
Phase 1 tests will skip if Docker is not installed.

### "GPG_KEY_NAME not set"
```bash
export GPG_KEY_NAME="Release Key (Redoubt)"
just sign-apt
```

### Arch Linux image not available in multipass
Use Docker fallback for AUR Phase 2 testing.

## References

- [Testing Improvement Plan](./TESTING-IMPROVEMENT-PLAN.md)
- [Testing Reassessment](./TESTING-REASSESSMENT.md)
- [Platform Support](../distribution/PLATFORM-SUPPORT.md)
