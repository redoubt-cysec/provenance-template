# DEVELOPER GUIDE — Using This Repo as a Template

Welcome! This guide shows you how to turn this template into your app with a reproducible, signed, and attested release pipeline.

## 0) What you get

- Deterministic builds (.pyz + sdist/wheel)
- GitHub provenance attestations + checksums signed via cosign keyless
- CycloneDX SBOM + OSV scan
- Hardened CI (egress control, pinned actions, no caches for release)
- From-source verification scripts + a Rebuilder workflow
- Optional distribution: Homebrew, Winget, OCI image (GHCR)

---

## 1) Prerequisites

- Python 3.11+
- Git + GitHub repository (created from this template)
- (Optional) GitHub CLI `gh`, `cosign` for local verification
- (Optional) Secrets if you want taps/winget:
  - `TAP_PUSH_TOKEN` (PAT with write to OWNER/homebrew-tap)
  - `WINGET_GITHUB_TOKEN` (PAT with PR rights to microsoft/winget-pkgs)

---

## 2) Clone and rename to your app

Replace placeholders with your values:

- `redoubt-cysec/provenance-demo` → your org/repo (e.g., acme/rocket-cli)
- CLI name: today it's `demo` (entry point), artifact name `client.pyz`
- Python package: today `demo_cli`

### A) Update project metadata

Edit [pyproject.toml](pyproject.toml):

- `name = "demo-secure-cli"` → your package name
- `description`, `authors`, `license`
- `[project.scripts]` entry point:

```toml
[project.scripts]
rocket = "rocket_cli.cli:main"
```

- If you change the package path, update wheel build target:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/rocket_cli"]
```

### B) Rename the package folder and CLI

```bash
mv src/demo_cli src/rocket_cli
# Edit imports & version
sed -i.bak 's/demo_cli/rocket_cli/g' src/rocket_cli/cli.py tests/test_cli.py
```

### C) Change the .pyz entry and artifact name

- In [scripts/build_pyz.sh](scripts/build_pyz.sh), update the zipapp module and output file:

```bash
python -m zipapp build/pyz/src -m "rocket_cli.cli:main" -o dist/rocket.pyz
```

- Throughout the repo (workflows/docs), replace `client.pyz` with `rocket.pyz`.

**Tip:** search for `client.pyz` and `demo_cli` and update all references (workflows, README, SUPPLY-CHAIN.md, verify scripts, Homebrew/Winget stubs).

---

## 3) Add your code & dependencies

- Put your CLI logic in `src/rocket_cli/`.
- Add runtime deps to [requirements.in](requirements.in) (keep it minimal).
- For deterministic installs in CI, you can lock with `pip-compile --generate-hashes` later if you grow deps.

---

## 4) Make CI yours

### A) Replace repo placeholders

Open these files and replace `redoubt-cysec/provenance-demo` and `client.pyz` with yours:

- `.github/workflows/*` (all of them)
- [SUPPLY-CHAIN.md](../security/SUPPLY-CHAIN.md), [QUICK-START.md](../../QUICK-START.md), [README.md](../../README.md)
- `scripts/verify_*.sh`
- `packaging/homebrew-tap/Formula/client.rb` (if using taps)

### B) Pin action SHAs (highly recommended)

Each `uses: ...@<PINNED_SHA>` must be a commit SHA. You can:

- Pin manually (from the action's Releases page → click "Use commit SHA").
- Or enable Renovate (already included) to keep them fresh.

### C) Harden-Runner allowlist (optional, recommended)

In `release.yml`, move from `egress-policy: audit` → `block` once stable, and list only endpoints you need (GitHub, Sigstore, Rekor, etc.).

---

## 5) Build & run locally

```bash
python -m venv .venv && source .venv/bin/activate
./scripts/build_pyz.sh
./dist/rocket.pyz --version
./dist/rocket.pyz Alice
```

---

## 6) Cut your first secure release

1. Commit your changes to main (PRs will run fast checks; main will run determinism & SBOM/OSV).
2. Tag a version (SemVer recommended):

```bash
git tag v0.1.0
git push origin v0.1.0
```

3. The Secure Release workflow will:
   - Build reproducibly (sdist/wheel/pyz)
   - Generate SBOM + vulnerability report
   - Compute SHA256SUMS and sign it with cosign keyless
   - Attest provenance for artifacts (GitHub attestation)
   - Publish a GitHub Release with verification commands embedded

---

## 7) Verification (what users do)

### Option A — GitHub attestation (recommended)

```bash
TAG=v0.1.0
REPO=redoubt-cysec/provenance-demo
curl -LO https://github.com/$REPO/releases/download/$TAG/rocket.pyz
gh attestation verify rocket.pyz --repo $REPO
```

### Option B — Checksums + optional cosign

```bash
curl -LO https://github.com/$REPO/releases/download/$TAG/SHA256SUMS
curl -LO https://github.com/$REPO/releases/download/$TAG/SHA256SUMS.bundle
sha256sum --check SHA256SUMS --ignore-missing

COSIGN_EXPERIMENTAL=1 cosign verify-blob \
  --bundle SHA256SUMS.bundle \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  --certificate-identity "https://github.com/$REPO/.github/workflows/Secure Release@refs/tags/$TAG" \
  SHA256SUMS
```

### From-source reproducible check

```bash
./scripts/verify_build.sh v0.1.0 OWNER REPO rocket.pyz
./scripts/verify_provenance.sh v0.1.0 OWNER REPO rocket.pyz
```

---

## 8) (Optional) Distribution channels

### Homebrew (tap)

- Create `OWNER/homebrew-tap` repo (public).
- Add repo secret `TAP_PUSH_TOKEN` with write access to that tap.
- Update `.github/workflows/update-homebrew-tap.yml`:
  - `TAP_REPO: OWNER/homebrew-tap`
  - `ASSET: rocket.pyz`
  - Update the Formula path/name (`Formula/rocket.rb`) and contents (URL/version/sha).
- On release, the workflow updates the tap with the sha from signed SHA256SUMS.

### Winget

- Add `WINGET_GITHUB_TOKEN` (PAT capable of PRs to microsoft/winget-pkgs).
- Update `.github/workflows/winget-publish.yml`:
  - `PACKAGE_ID: OWNER.REPO.Rocket`
  - `ASSET: rocket.pyz`
- On release, it opens a PR to winget with the right SHA256.

### OCI (GHCR)

- Use `oci-release.yml`.
- The job builds a minimal image that runs your .pyz, pushes to GHCR, signs with cosign keyless, and attaches the SBOM.

---

## 9) Versioning & changelog

- Follow SemVer and tag `vX.Y.Z`.
- Generate release notes via GitHub automatically (already enabled).
- If you want a CHANGELOG.md, add it and link in pyproject.toml readme.

---

## 10) Common customizations

- **Rename entry point:** change `[project.scripts]` in pyproject.toml and the zipapp `-m` target in scripts/build_pyz.sh.
- **Add dependencies:** put them in requirements.in; the SBOM and OSV scan will include them automatically.
- **Add tests:** expand tests/ and wire your preferred runner (e.g., pytest) in PR workflows if desired.
- **Harden further:** enable scheduled base-image scan, nightly OSV on latest release, Scorecards — workflows already provided (just replace placeholders and commit).

---

## 11) Troubleshooting

### Attestation verify fails

- Update `gh` CLI; verify you used the exact release artifact (no re-uploads).
- Check the identity string in the command matches your repo/workflow name.

### Checksum mismatch

- Redownload both artifact and SHA256SUMS.
- Ensure you didn't modify the artifact (e.g., chmod + LF conversions on Windows shells can't alter the zipapp, but guard against unzip/re-zip).

### Rebuilder workflow shows no matching hashes

- Confirm the tag exists and matches the release.
- Ensure `SOURCE_DATE_EPOCH` derives from that tag's commit.
- Verify your local changes aren't uncommitted (the CI checks out the tag clean).

### Harden-Runner breaks release

- Start with `egress-policy: audit` to collect required endpoints.
- Add allowlist entries, then switch to `block`.

---

## 12) Security ops tips (keep it sharp)

- Protect main + `v*` tags; require reviews and status checks.
- Keep actions pinned to SHAs; use Renovate to rotate.
- Don't enable caches in release jobs (keeps builds hermetic).
- Rotate base image digests and run weekly Trivy (template provided).
- Treat Homebrew/Winget tokens as sensitive; scope tightly.

---

## 13) Quick "rename checklist"

- Replace `redoubt-cysec/provenance-demo` everywhere
- `client.pyz` → `rocket.pyz` (or your name)
- `demo_cli` → `rocket_cli` (package)
- `[project.scripts] demo = ...` → `rocket = ...`
- Update scripts/build_pyz.sh zipapp entry + output file
- Update workflows to use your artifact name
- Update SUPPLY-CHAIN/README verify commands
- (Optional) Tap/winget workflow env + secrets
- Pin action SHAs

---

## 14) Ship it 🚀

When you're ready:

```bash
git tag v0.1.0
git push origin v0.1.0
# Find your signed, attested release under GitHub → Releases
```

---

## 15) Roadmap: Additional Distribution Channels

The following distribution channels are planned for future releases. Contributions welcome!

### Package Managers & Registries

- **PyPI** - Python Package Index distribution (wheel/sdist already built, just need twine upload workflow)
- **Scoop** - Windows command-line installer (similar workflow to Homebrew tap)
- **Snap** - Ubuntu/Linux snap packages with confinement
- **Flatpak** - Cross-distro Linux packaging with sandboxing
- **APT/DEB** - Debian/Ubuntu repository hosting
- **RPM/YUM** - RedHat/Fedora/CentOS repository hosting
- **AUR** - Arch User Repository (community-maintained)
- **Nix/nixpkgs** - Nix package manager integration
- **Chocolatey** - Windows package manager alternative
- **asdf plugin** - Version manager plugin (growing adoption)

### Direct Distribution

- **NPM wrapper** - Distribute via npm for JavaScript ecosystem (like Rust CLIs)
- **curl | sh installer** - Self-hosted install script with verification
- **Platform-specific binaries** - Auto-generate download table with OS detection
- **GitHub Action** - Wrap CLI as a reusable GitHub Action

### Cloud & Container

- **Docker Hub** - Mirror GHCR images for broader discoverability
- **AWS Lambda Layer** - Package as a Lambda layer for serverless use
- **Public artifact registries** - GitLab Container Registry, Azure Container Registry, AWS ECR Public

### Integration Priorities

**Phase 1 (Easiest wins):**

1. PyPI - Already have wheel artifacts
2. Scoop - Similar to existing Homebrew workflow
3. curl | sh installer - Simple verification script

**Phase 2 (Medium complexity):**

1. asdf plugin - Growing developer adoption
2. NPM wrapper - Reach JavaScript developers
3. Snap/Flatpak - Linux desktop users

**Phase 3 (Advanced):**

1. APT/DEB + RPM repositories - Enterprise Linux
2. Lambda Layer - Serverless ecosystem
3. Homebrew core - Graduate from tap (requires traction)

Want to contribute one of these? Open an issue or PR!

---

## Need Help?

If you need this guide tailored with your actual CLI name, package name, and org/repo baked in, update the placeholders throughout the repository and this guide with your specific values.
