# GitHub Secrets Setup Guide

## Essential Secrets (Required)

### 1. CACHIX_AUTH_TOKEN ⭐ PRIORITY

**Purpose**: Enables Nix binary caching (makes Nix installs 10x faster)

**How to get it**:
```bash
# Option A: Sign up at cachix.org
1. Go to https://app.cachix.org
2. Sign in with GitHub
3. Create a new cache: "provenancedemo" (or your preferred name)
4. Go to Account → Create Token
5. Copy the token

# Option B: Use public cache (no auth needed)
# Skip this secret and the workflow will use Magic Nix Cache only
```

**Add to GitHub**:
- Name: `CACHIX_AUTH_TOKEN`
- Value: `eyJhbGc...` (your token)

---

### 2. CACHIX_CACHE_NAME

**Purpose**: Name of your Cachix cache

**Value**: `provenancedemo` (or whatever name you chose)

**Add to GitHub**:
- Name: `CACHIX_CACHE_NAME`
- Value: `provenancedemo`

---

### 3. TAP_GITHUB_TOKEN ⭐ PRIORITY

**Purpose**: Allows Homebrew workflow to push to your homebrew-tap repository

**How to get it**:
```bash
1. Go to GitHub → Settings → Developer settings
2. Personal access tokens → Tokens (classic) → Generate new token
3. Name: "Homebrew Tap Updater"
4. Expiration: No expiration (or 1 year)
5. Scopes:
   ✓ repo (full control)
   ✓ workflow (if you want to update workflows)
6. Generate token
7. Copy the token (starts with ghp_)
```

**Add to GitHub**:
- Name: `TAP_GITHUB_TOKEN`
- Value: `ghp_xxxxxxxxxxxx`

---

### 4. PYPI_TOKEN ⭐ PRIORITY

**Purpose**: Publishes package to production PyPI (pypi.org)

**How to get it**:
```bash
1. Go to https://pypi.org/manage/account/login/
2. Navigate to Account settings → API tokens
3. Click "Add API token"
4. Name: "GitHub Actions - provenance-demo"
5. Scope: "Entire account" (or specific to provenance-demo project)
6. Copy the token (starts with pypi-)
```

**Add to GitHub**:
- Name: `PYPI_TOKEN`
- Value: `pypi-AgEIcHlwaS5vcmcC...`

---

### 5. TESTPYPI_TOKEN ⭐ PRIORITY

**Purpose**: Publishes package to TestPyPI (test.pypi.org) for testing before production

**How to get it**:
```bash
1. Go to https://test.pypi.org/manage/account/login/
2. Navigate to Account settings → API tokens
3. Click "Add API token"
4. Name: "GitHub Actions - provenance-demo"
5. Scope: "Entire account" (or specific project)
6. Copy the token (starts with pypi-)
```

**Add to GitHub**:
- Name: `TESTPYPI_TOKEN`
- Value: `pypi-AgEIcHlwaS5vcmcC...`

---

### 6. SNAPCRAFT_STORE_CREDENTIALS ⭐ PRIORITY

**Purpose**: Publishes snap package to Snap Store (snapcraft.io)

**How to get it**:
```bash
# 1. Login to snapcraft (one-time setup)
snapcraft login

# 2. Export credentials
snapcraft export-login snapcraft-credentials.txt

# 3. View the credentials file (this is what goes in the secret)
cat snapcraft-credentials.txt
```

**Add to GitHub**:
- Name: `SNAPCRAFT_STORE_CREDENTIALS`
- Value: `[entire contents of snapcraft-credentials.txt]`

**Security Note**: After adding to GitHub secrets, delete the local file:
```bash
rm snapcraft-credentials.txt
```

---

## Optional Secrets (For Enhanced Security)

### 7. GPG_PRIVATE_KEY (Optional)

**Purpose**: Signs APT/RPM packages with GPG

**How to get it**:
```bash
# If you have a GPG key:
gpg --list-secret-keys
gpg --armor --export-secret-key YOUR_KEY_ID

# If you need to create one:
gpg --full-generate-key
# Choose: RSA and RSA, 4096 bits, no expiration
# Real name: Borduas Holdings Ltd.
# Email: packages@borduasholdings.com
```

**Add to GitHub**:
- Name: `GPG_PRIVATE_KEY`
- Value: `-----BEGIN PGP PRIVATE KEY BLOCK-----...`

---

### 8. GPG_PASSPHRASE (Optional)

**Purpose**: Passphrase for GPG key

**Add to GitHub**:
- Name: `GPG_PASSPHRASE`
- Value: `your-passphrase`

---

## Quick Setup Script

You can also set secrets via GitHub CLI:

```bash
# Install gh CLI if needed
brew install gh

# Login
gh auth login

# Set secrets
gh secret set CACHIX_AUTH_TOKEN --repo redoubt-cysec/provenance-demo
gh secret set CACHIX_CACHE_NAME --repo redoubt-cysec/provenance-demo --body "redoubt"

gh secret set TAP_GITHUB_TOKEN --repo redoubt-cysec/provenance-demo
```

---

## Testing Without Secrets

You can create a release **without** secrets and most things will still work:

- ✅ .pyz build
- ✅ AppImage build
- ✅ Nix build (with Magic Nix Cache)
- ✅ AUR validation
- ✅ Docker build (uses GITHUB_TOKEN automatically)
- ⏩ Homebrew (will skip without TAP_GITHUB_TOKEN)
- ⏩ PyPI (will skip without PYPI_TOKEN and TESTPYPI_TOKEN)
- ⏩ Snap Store (will skip without SNAPCRAFT_STORE_CREDENTIALS)
- ⏩ Cachix (will use Magic Nix Cache only)
- ⏩ GPG signing (will skip without keys)

---

## Verification

After adding secrets, they should appear in:
https://github.com/redoubt-cysec/provenance-template/settings/secrets/actions

You should see:
- ✅ CACHIX_AUTH_TOKEN (if added)
- ✅ CACHIX_CACHE_NAME (if added)
- ✅ TAP_GITHUB_TOKEN (if added)
- ✅ PYPI_TOKEN (if added)
- ✅ TESTPYPI_TOKEN (if added)
- ✅ SNAPCRAFT_STORE_CREDENTIALS (if added)
- ✅ GPG_PRIVATE_KEY (if added)
- ✅ GPG_PASSPHRASE (if added)
- Plus GITHUB_TOKEN (automatic, always present)
