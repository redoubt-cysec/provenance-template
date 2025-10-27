# Quick Start Guide

## Setup Instructions

### 1. Create Repository from Template

1. Click "Use this template" on GitHub → "Create a new repository"
2. Clone your new repository locally

### 2. Replace Placeholders

You need to replace these placeholders in workflow files:

- `jonathanborduas/redoubt-release-template` - Your GitHub username/org and repository name
- `<PINNED_SHA>` - Pin all GitHub Actions to specific commit SHAs
- `<PINNED_DIGEST>` - Pin container image to specific digest

#### Finding Pinned SHAs

For each action, find the latest SHA:

```bash
# Example for actions/checkout@v4
gh api repos/actions/checkout/commits/main --jq '.sha'
```

Or use a tool like [pin-github-action](https://github.com/mheap/pin-github-action).

#### Finding Container Digest

```bash
# For python:3.11-slim
docker pull python:3.11-slim
docker inspect python:3.11-slim --format='{{index .RepoDigests 0}}'
```

### 3. Configure Secrets (Optional)

If you want to publish to Homebrew or Winget, add these repository secrets:

- `TAP_PUSH_TOKEN` - Personal Access Token with write access to `OWNER/homebrew-tap`
- `WINGET_GITHUB_TOKEN` - PAT for creating PRs to microsoft/winget-pkgs

Go to: Settings → Secrets and variables → Actions → New repository secret

### 4. Create Production Environment (Recommended)

For release protection:

1. Settings → Environments → New environment → "production"
2. Add required reviewers (optional but recommended)
3. The release workflow will wait for approval before deploying

### 5. Push First Release

```bash
# Customize the CLI if desired, then commit
git add -A
git commit -m "Initial commit from template"
git push origin main

# Wait for main-verify workflow to pass, then tag
git tag v0.1.0
git push origin v0.1.0
```

The release workflow will:

1. Build deterministically
2. Generate SBOM and vulnerability reports
3. Sign checksums with cosign
4. Create GitHub provenance attestations
5. Create a GitHub release with all artifacts

### 6. Verify Your Release

```bash
TAG=v0.1.0
REPO=YOUR_OWNER/YOUR_REPO

# Download
curl -LO https://github.com/$REPO/releases/download/$TAG/client.pyz
chmod +x client.pyz

# Run
./client.pyz --version
./client.pyz World

# Verify attestation
gh attestation verify client.pyz --repo $REPO
```

## Next Steps

- Customize `src/demo_cli/cli.py` with your actual CLI logic
- Add dependencies to `requirements.in`
- Update `pyproject.toml` with your package metadata
- Add tests in `tests/`
- Update documentation

## Maintenance

- **Update dependencies**: Edit `requirements.in`, rebuild
- **New release**: Tag with semantic version (e.g., `v1.0.1`)
- **Check security**: Scorecards runs weekly, scan-latest-release runs daily
- **Verify reproducibility**: Run the rebuilder workflow manually for any tag

## Troubleshooting

### Build fails on first run

- Ensure `rsync` is available (install via package manager if needed)
- Check Python 3.11+ is available

### Release workflow fails

- Verify you've created the "production" environment
- Check you have write permissions for releases
- Ensure no required secrets are missing if using optional workflows

### Verification fails

- Ensure you've replaced `jonathanborduas/redoubt-release-template` placeholders
- GitHub CLI must be authenticated: `gh auth login`
- For cosign verification, ensure cosign is installed: `brew install cosign` or similar
