# Configuration Decisions

## 1. Repository Name & Purpose

### Decision: [CHOOSE ONE]

- [ ] **Option A: Keep as Template**
  - Repository name: `redoubt-release-template`
  - Artifact names: `redoubt-release-template.pyz`
  - Docker image: `ghcr.io/borduas-holdings/redoubt-release-template`
  - Purpose: Reference implementation for others to copy
  - Action: Keep current naming

- [x] **Option B: Make This Your Product** ✅ RECOMMENDED
  - Repository name: `redoubt` (rename repo)
  - Artifact names: `redoubt.pyz`
  - Docker image: `ghcr.io/borduas-holdings/redoubt`
  - Purpose: Your actual supply chain security tool
  - Action: Rename everything to "redoubt"

### If Option B (Recommended):

**Changes needed**:
1. Rename repository in GitHub settings
2. Update all workflow files
3. Update package names
4. Update Docker image names
5. Update documentation

**Script to update names**:
```bash
# I can create a script to do this automatically
# Find/replace "redoubt-release-template" → "redoubt"
```

---

## 2. Repository Visibility

### Decision: [CHOOSE ONE]

- [ ] **Keep Private**
  - Use case: Internal/proprietary tool
  - Limitations: Auth required for Homebrew, Docker
  - Action: Keep current settings

- [x] **Make Public** ✅ RECOMMENDED
  - Use case: Open-source supply chain security template
  - Benefits: No auth needed, community contributions, portfolio
  - Action: Settings → Change visibility to Public

### Why Public is Recommended:

✅ Better for supply chain security (transparency)
✅ Easier distribution (no auth for installs)
✅ Community contributions
✅ Great portfolio piece
✅ Free GitHub Actions minutes (more generous)
✅ Homebrew tap works without PAT

**⚠️ Before making public**:
- [ ] Remove any secrets from git history
- [ ] Review all documentation
- [ ] Ensure no proprietary code
- [ ] Add clear LICENSE file

---

## 3. Signing Configuration

### Nix (Cachix)

- [x] **Cachix-managed signing** ✅ RECOMMENDED
  - Cachix handles key management
  - Automatic signing
  - Secure (keys never leave Cachix)
  - Free for public caches

Setup:
```bash
1. Create cache at https://app.cachix.org
2. Enable "Signing" option when creating cache
3. Add CACHIX_AUTH_TOKEN to GitHub Secrets
4. Done! Cachix signs automatically
```

Alternative:
- [ ] **Self-signed GPG for Nix**
  - More control, more complexity
  - Use if you want unified GPG key across all platforms

---

### APT/RPM Packages

- [x] **Self-signed GPG** ✅ RECOMMENDED
  - Standard practice for package repos
  - Users verify with your public key

Setup:
```bash
# Generate GPG key
gpg --full-generate-key
# Export private key for GitHub Secret
gpg --armor --export-secret-key YOUR_KEY_ID > private.key
# Add to GitHub Secrets: GPG_PRIVATE_KEY
```

Alternative:
- [ ] **No signing (trusted=yes)**
  - Simpler but less secure
  - Users must add [trusted=yes] to sources

---

## 4. Cachix Cache Visibility

### Decision: [CHOOSE ONE]

- [x] **Public cache** ✅ RECOMMENDED (if repo is public)
  - Anyone can use your binary cache
  - Faster installs for users
  - Free tier: 5GB storage, 10GB/month bandwidth

- [ ] **Private cache**
  - Only for paid Cachix plans
  - Users need auth token to access
  - Use if: proprietary binaries

---

## Quick Start Configuration

### Minimal Setup (5 minutes):

1. **Make repo public**: Settings → Change visibility → Public
2. **Create Cachix account**: https://app.cachix.org
   - Create cache: "redoubt"
   - Enable signing: ✓
   - Copy auth token
3. **Add GitHub Secrets**:
   - `CACHIX_AUTH_TOKEN`: [your token]
   - `CACHIX_CACHE_NAME`: `redoubt`
4. **Create test release**: `git tag v0.0.1 && git push origin v0.0.1`

### Full Setup with Homebrew (10 minutes):

All of above, plus:
5. **Create PAT**: GitHub → Settings → Developer settings → Tokens
   - Scope: `repo`
6. **Add GitHub Secret**:
   - `TAP_GITHUB_TOKEN`: [your PAT]
7. **Create homebrew-tap repo**: https://github.com/Borduas-Holdings/homebrew-tap

---

## Summary of Recommendations

| Item | Recommendation | Reason |
|------|---------------|--------|
| **Name** | `redoubt` (not template) | Cleaner, this is your product now |
| **Visibility** | Public | Better distribution, no auth issues |
| **Nix Signing** | Cachix-managed | Easier, more secure |
| **APT/RPM Signing** | Self-signed GPG | Standard practice |
| **Cachix Cache** | Public | Free, faster for users |

---

## Next Steps

1. Make decisions above
2. Rename repository (if Option B)
3. Make repository public
4. Set up Cachix with signing
5. Add secrets to GitHub
6. Create test release v0.0.1
7. Test installation from each platform
