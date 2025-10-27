# Publishing Guide - Token Requirements by Platform

This guide explains what tokens and accounts you need to publish to each platform.

## Quick Reference

| Platform | Phase 2 (Private) | Phase 3 (Public) | Required Token/Account |
|----------|-------------------|------------------|------------------------|
| **Homebrew** | ✅ `gh` CLI only | PR to homebrew-core | GitHub account |
| **PyPI** | ✅ Test PyPI token | PyPI token | [pypi.org](https://pypi.org) account |
| **Docker** | ✅ `gh` CLI (GHCR) | Docker Hub token | [hub.docker.com](https://hub.docker.com) account |
| **Snap** | ✅ Snapcraft login | Snapcraft login | [snapcraft.io](https://snapcraft.io) account |
| **APT** | ✅ `gh` CLI only | PPA or Debian | Launchpad account |
| **RPM** | ✅ `gh` CLI only | Fedora review | FAS account |
| **Scoop** | ✅ `gh` CLI only | PR to extras | GitHub account |
| **WinGet** | ⚠️ Manual testing | PR to winget-pkgs | GitHub account |
| **Chocolatey** | ⚠️ No Phase 2 | Chocolatey API key | [chocolatey.org](https://community.chocolatey.org) account |
| **Flatpak** | ⚠️ No Phase 2 | PR to Flathub | GitHub account |
| **AppImage** | ✅ Local build | Host on GitHub | GitHub account |
| **AUR** | ⚠️ No Phase 2 | AUR account + SSH | [aur.archlinux.org](https://aur.archlinux.org) account |
| **Nix** | ⚠️ No Phase 2 | PR to nixpkgs | GitHub account |

**Legend:**

- ✅ Full Phase 2 support with automated testing
- ⚠️ Limited or no Phase 2 support
- **Phase 2**: Private/testing distribution
- **Phase 3**: Public production release

---

## Phase 1: Local Build Testing

**Required:** Nothing! Just build and test locally.

```bash
# Build
./scripts/build_pyz.sh

# Test locally
./dist/redoubt-release-template.pyz --version

# Run tests
uv run pytest tests/ -m "not slow and not integration"
```

**No tokens, no accounts, no configuration needed.**

---

## Phase 2: Private Distribution Testing

### ✅ Required for ALL Phase 2 Testing

**GitHub CLI (`gh`)**

```bash
# Install
brew install gh          # macOS
sudo apt install gh      # Linux

# Authenticate
gh auth login

# Verify
gh auth status
```

This single authentication enables:

- Homebrew private tap creation
- Docker push to GHCR
- APT repository (GitHub Pages)
- RPM repository (GitHub Pages)
- Scoop bucket creation

### ✅ Platform-Specific Requirements

#### Test PyPI (Python packages)

**Required:** Test PyPI account and token

**Setup:**

1. Register: <https://test.pypi.org/account/register/>
2. Verify email
3. Create token: <https://test.pypi.org/manage/account/token/>
   - Scope: "Entire account" (first upload) or "Project" (after first upload)
4. Add to `~/.pypirc`:

```ini
[testpypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcC...your-token
```

**Test:**

```bash
./scripts/phase2-testing/setup-test-pypi.sh
./scripts/phase2-testing/test-test-pypi-vm.sh
```

**If missing:** ⚠️ Test PyPI publishing will fail, but Snap and Homebrew still work

---

#### Snapcraft (Snap Store)

**Required:** Snapcraft account and registered snap name

**Setup:**

1. Register: <https://snapcraft.io/account>
2. Install: `sudo snap install snapcraft --classic`
3. Login: `snapcraft login`
4. Register name: `snapcraft register redoubt-release-template`
   - Name must be unique globally
   - Request takes ~1 day for approval

**Test:**

```bash
./scripts/phase2-testing/setup-snap-edge.sh
./scripts/phase2-testing/test-snap-edge-vm.sh
```

**If missing:** ⚠️ Snap publishing will fail. Skip with:

```bash
./scripts/phase2-testing/run-all-phase2-tests.sh --setup homebrew pypi docker apt rpm
```

---

#### Docker/GHCR (Container Registry)

**Required:** GitHub authentication only (uses `gh` CLI)

**Setup:**

```bash
# Already done if you ran: gh auth login

# Verify Docker access
gh auth token | docker login ghcr.io -u YOUR_USERNAME --password-stdin
```

**Test:**

```bash
./scripts/phase2-testing/setup-docker-registry.sh
./scripts/phase2-testing/test-docker-registry-vm.sh
```

**If missing:** ⚠️ Docker GHCR push will fail

---

#### Homebrew Tap (macOS/Linux)

**Required:** GitHub authentication only (uses `gh` CLI)

**Setup:**

```bash
# Already done if you ran: gh auth login
```

**Test:**

```bash
./scripts/phase2-testing/setup-homebrew-tap.sh
./scripts/phase2-testing/test-homebrew-tap-vm.sh
```

**If missing:** ⚠️ Cannot test Homebrew installation

---

#### APT Repository (Debian/Ubuntu)

**Required:**

- GitHub authentication (uses `gh` CLI)
- `dpkg-deb` for building packages

**Setup:**

```bash
# macOS
brew install dpkg

# Ubuntu/Debian
sudo apt install dpkg-dev
```

**Test:**

```bash
./scripts/phase2-testing/setup-apt-repo.sh
./scripts/phase2-testing/test-apt-repo-vm.sh
```

**If missing:** ⚠️ APT repository creation will fail

---

#### RPM Repository (Fedora/RHEL)

**Required:**

- GitHub authentication (uses `gh` CLI)
- `rpmbuild` and `createrepo_c`

**Setup:**

```bash
# macOS
brew install rpm createrepo_c

# Fedora/RHEL
sudo dnf install rpm-build createrepo_c

# Ubuntu/Debian
sudo apt install rpm createrepo-c
```

**Test:**

```bash
./scripts/phase2-testing/setup-rpm-repo.sh
./scripts/phase2-testing/test-rpm-repo-vm.sh
```

**If missing:** ⚠️ RPM repository creation will fail

---

#### Scoop Bucket (Windows)

**Required:** GitHub authentication only (uses `gh` CLI)

**Setup:**

```bash
# Already done if you ran: gh auth login
```

**Test:**

```bash
./scripts/phase2-testing/setup-scoop-bucket.sh
# Then manually test in Windows VM
```

**If missing:** ⚠️ Scoop bucket creation will fail

---

### ⚠️ Platforms WITHOUT Phase 2 Testing

These platforms require public releases (Phase 3) or manual testing:

- **WinGet**: Requires actual GitHub release, then PR to microsoft/winget-pkgs
- **Chocolatey**: No testing environment available
- **Flatpak/Flathub**: Requires PR to Flathub
- **AUR**: Can only test with real AUR upload
- **Nix/nixpkgs**: Requires PR to NixOS/nixpkgs

**Workaround:** Use Phase 1 (local build) testing instead

---

## Phase 3: Public Release Requirements

### PyPI (Production)

**Required:** PyPI production token

**Setup:**

1. Register: <https://pypi.org/account/register/>
2. Create project-scoped token: <https://pypi.org/manage/account/token/>
3. Add to GitHub Secrets:
   - Name: `PYPI_TOKEN`
   - Value: `pypi-AgEIcHlwaS5vcmcC...`

**Publish:**

```bash
# Manual
twine upload dist/*

# GitHub Actions (automatic on tag push)
git tag v0.1.0
git push origin v0.1.0
```

---

### Docker Hub

**Required:** Docker Hub account and token

**Setup:**

1. Register: <https://hub.docker.com/signup>
2. Create token: <https://hub.docker.com/settings/security>
3. Add to GitHub Secrets:
   - Name: `DOCKERHUB_USERNAME`
   - Value: `your-username`
   - Name: `DOCKERHUB_TOKEN`
   - Value: `dckr_pat_...`

**Publish:**

```bash
echo $DOCKERHUB_TOKEN | docker login -u $DOCKERHUB_USERNAME --password-stdin
docker push your-username/redoubt-release-template:latest
```

---

### Snap Store (Stable)

**Required:** Snapcraft account (same as Phase 2)

**Publish:**

```bash
# Promote from edge to stable
snapcraft promote redoubt-release-template --from-channel edge --to-channel stable
```

---

### Homebrew Core

**Required:** GitHub account, public release

**Process:**

1. Create public GitHub release
2. Submit PR to homebrew-core:

```bash
brew create --tap homebrew/core \
  https://github.com/Borduas-Holdings/redoubt-release-template/releases/download/v0.1.0/redoubt-release-template.pyz
```

3. Wait for review (1-7 days)

**Documentation:** <https://docs.brew.sh/Adding-Software-to-Homebrew>

---

### Chocolatey

**Required:** Chocolatey account and API key

**Setup:**

1. Register: <https://community.chocolatey.org/account/Register>
2. Get API key: <https://community.chocolatey.org/account>
3. Add to GitHub Secrets:
   - Name: `CHOCOLATEY_API_KEY`

**Publish:**

```bash
choco push redoubt-release-template.nupkg \
  --source https://push.chocolatey.org/ \
  --api-key $CHOCOLATEY_API_KEY
```

---

### WinGet

**Required:** GitHub account, public release

**Process:**

1. Create public GitHub release
2. Use wingetcreate:

```bash
wingetcreate new \
  --url https://github.com/Borduas-Holdings/redoubt-release-template/releases/download/v0.1.0/redoubt-release-template.pyz
```

3. Submit PR to microsoft/winget-pkgs
4. Wait for review (1-5 days)

**Documentation:** <https://learn.microsoft.com/en-us/windows/package-manager/package/manifest>

---

### Flatpak/Flathub

**Required:** GitHub account

**Process:**

1. Submit to Flathub: <https://github.com/flathub/flathub/wiki/App-Submission>
2. Create manifest in flathub repo
3. Submit PR
4. Wait for review (1-14 days)

**Documentation:** <https://docs.flathub.org/docs/for-app-authors/submission>

---

### AUR (Arch User Repository)

**Required:** AUR account, SSH key

**Setup:**

1. Register: <https://aur.archlinux.org/register/>
2. Add SSH key: <https://aur.archlinux.org/ssh-keys>
3. Create PKGBUILD
4. Push to AUR:

```bash
git remote add aur ssh://aur@aur.archlinux.org/redoubt-release-template.git
git push aur master
```

**Documentation:** <https://wiki.archlinux.org/title/AUR_submission_guidelines>

---

### Nix/nixpkgs

**Required:** GitHub account

**Process:**

1. Fork NixOS/nixpkgs
2. Add package derivation to `pkgs/`
3. Test with `nix-build`
4. Submit PR
5. Wait for review (1-14 days)

**Documentation:** <https://nixos.org/manual/nixpkgs/stable/#chap-submitting-changes>

---

## Token Security Best Practices

### 1. Token Scopes (Principle of Least Privilege)

| Token | Minimum Scope | Why |
|-------|---------------|-----|
| PyPI | Project-specific | Limits damage if leaked |
| GitHub | `repo`, `read:packages` | No admin access |
| Docker Hub | Read/Write | No delete permissions |
| Chocolatey | Package-specific | After first upload |

### 2. Token Storage

**DO:**

- ✅ Store in GitHub Secrets/Environments
- ✅ Use `.env` file (in `.gitignore`)
- ✅ Use password managers
- ✅ Rotate regularly (every 90 days)
- ✅ Enable 2FA on all accounts

**DON'T:**

- ❌ Commit to git
- ❌ Share in Slack/Discord
- ❌ Store in plaintext files
- ❌ Use broad-scope tokens

### 3. GitHub Environments (Recommended)

Create protected environment for releases:

```yaml
# Settings → Environments → New environment
Name: release

Protection rules:
- Required reviewers: 1
- Wait timer: 5 minutes
- Deployment branches: tags (v*)

Secrets:
- PYPI_TOKEN
- DOCKERHUB_TOKEN
- CHOCOLATEY_API_KEY
```

Use in workflow:

```yaml
jobs:
  release:
    environment: release  # Requires approval
    steps:
      - name: Publish to PyPI
        env:
          PYPI_TOKEN: ${{ secrets.PYPI_TOKEN }}
```

---

## Testing Checklist

### Phase 1: Local (No tokens)

- [ ] Build succeeds: `./scripts/build_pyz.sh`
- [ ] Binary runs: `./dist/redoubt-release-template.pyz --version`
- [ ] Tests pass: `uv run pytest tests/ -m "not slow"`

### Phase 2: Private (Minimal tokens)

- [ ] GitHub CLI authenticated: `gh auth status`
- [ ] Homebrew tap works: `./scripts/phase2-testing/test-homebrew-tap-vm.sh`
- [ ] Test PyPI works (if token available): `./scripts/phase2-testing/test-test-pypi-vm.sh`
- [ ] Docker GHCR works: `./scripts/phase2-testing/test-docker-registry-vm.sh`
- [ ] APT repo works: `./scripts/phase2-testing/test-apt-repo-vm.sh`
- [ ] RPM repo works: `./scripts/phase2-testing/test-rpm-repo-vm.sh`

### Phase 3: Public (Platform tokens)

- [ ] PyPI production token added to GitHub Secrets
- [ ] Docker Hub token added to GitHub Secrets
- [ ] Tag pushed: `git tag v0.1.0 && git push origin v0.1.0`
- [ ] Release workflow succeeds
- [ ] Artifacts published and downloadable
- [ ] Platform PRs submitted (Homebrew, WinGet, etc.)

---

## Quick Start

**Minimal setup (Phase 2 testing):**

```bash
# 1. Install GitHub CLI
brew install gh  # macOS
sudo apt install gh  # Linux

# 2. Authenticate
gh auth login

# 3. Test all platforms
./scripts/phase2-testing/run-all-phase2-tests.sh --setup homebrew docker apt rpm

# 4. If you have Test PyPI token, add it
echo "TESTPYPI_TOKEN=pypi-..." >> .env
./scripts/phase2-testing/run-all-phase2-tests.sh --setup pypi
```

**For production releases:**

1. Add tokens to GitHub Secrets (see platform sections above)
2. Create release: `gh release create v0.1.0 --generate-notes`
3. GitHub Actions will handle the rest

---

## Troubleshooting

### "gh: command not found"

```bash
brew install gh && gh auth login
```

### "Permission denied" for GitHub CLI

```bash
gh auth refresh -s write:packages,repo
```

### "Test PyPI upload failed"

Check `~/.pypirc` configuration:

```ini
[testpypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcC...
```

### "Snap name not registered"

```bash
snapcraft register redoubt-release-template
# Wait ~24 hours for approval
```

### "Docker push denied"

```bash
gh auth token | docker login ghcr.io -u YOUR_USERNAME --password-stdin
```

---

## Summary: What You Actually Need

### To get started (Phase 1)

- **Nothing!** Just build and test locally

### For Phase 2 testing (recommended)

- **GitHub CLI** (`gh auth login`) - Required
- **Test PyPI token** (optional) - Only if testing PyPI
- **Snapcraft account** (optional) - Only if testing Snap

### For Phase 3 production

- **PyPI token** - For Python packages
- **Docker Hub token** - For Docker images
- **Platform-specific accounts** - As needed per platform

**Most platforms don't require tokens** - they use standard GitHub PR workflows!
