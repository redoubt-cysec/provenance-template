# GPG Signing Quick Start

**Time**: 10-15 minutes
**Difficulty**: Easy
**Prerequisites**: GPG installed locally

This is a quick-start guide to get GPG signing working for APT and RPM repositories.

For complete documentation, see: [GPG-KEY-MANAGEMENT.md](GPG-KEY-MANAGEMENT.md)

---

## Step 1: Generate GPG Key (5 minutes)

Run the automated key generation script:

```bash
./scripts/ops/generate-gpg-key.sh
```

The script will prompt you for:
- Package name (default: redoubt)
- Your name (default: Release Manager)
- Your email (default: noreply@example.com)
- Key validity (default: 2y)
- Passphrase (**REQUIRED** for production)

**Output files** in `gpg-keys/`:
```
gpg-keys/
├── release-public-key.asc      # Distribute to users
├── release-private-key.asc     # NEVER commit!
├── release-private-key.b64     # For GitHub Secrets
└── key-fingerprint.txt         # For verification
```

**⚠️ Important**: These files are automatically ignored by git (`.gitignore`). Keep them secure!

---

## Step 2: Add GitHub Secrets (2 minutes)

Go to: `https://github.com/OWNER/REPO/settings/secrets/actions`

Add 3 secrets:

| Secret Name | Value | Where to find it |
|-------------|-------|------------------|
| `GPG_PRIVATE_KEY` | Base64-encoded private key | Copy from `gpg-keys/release-private-key.b64` |
| `GPG_KEY_NAME` | Key identifier (uid) | Shown at end of generation script |
| `GPG_PASSPHRASE` | Passphrase you entered | Your passphrase |

**Example values**:
```bash
# GPG_KEY_NAME example:
Release Manager (redoubt Release Key) <noreply@example.com>

# GPG_PRIVATE_KEY example (abbreviated):
LS0tLS1CRUdJTiBQR1AgUFJJVkFURSBLRVkgQkxPQ0stLS0tLQp...

# GPG_PASSPHRASE example:
your-secure-passphrase-here
```

---

## Step 3: Use in GitHub Actions (3 minutes)

Add this to your workflow (`.github/workflows/release.yml`):

```yaml
name: Release

on:
  push:
    tags: ['v*']

jobs:
  build-and-sign:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup GPG
        env:
          GPG_PRIVATE_KEY: ${{ secrets.GPG_PRIVATE_KEY }}
          GPG_KEY_NAME: ${{ secrets.GPG_KEY_NAME }}
          GPG_PASSPHRASE: ${{ secrets.GPG_PASSPHRASE }}
        run: ./scripts/release/setup-gpg-in-ci.sh

      - name: Build packages
        run: |
          # Your build steps here
          ./scripts/release/build-apt-repo.sh
          ./scripts/release/build-rpm.sh

      - name: Sign APT repository
        env:
          GPG_KEY_NAME: ${{ secrets.GPG_KEY_NAME }}
          GPG_PASSPHRASE: ${{ secrets.GPG_PASSPHRASE }}
        run: ./scripts/release/sign-apt-repo.sh dist/deb-repo

      - name: Sign RPM packages
        env:
          GPG_KEY_NAME: ${{ secrets.GPG_KEY_NAME }}
          GPG_PASSPHRASE: ${{ secrets.GPG_PASSPHRASE }}
        run: ./scripts/release/sign-rpm.sh dist/rpm
```

---

## Step 4: Test Locally (Optional, 5 minutes)

Before pushing to CI, test signing locally:

### Set environment variables:

```bash
# From the output of generate-gpg-key.sh:
export GPG_KEY_NAME="Release Manager (redoubt Release Key) <noreply@example.com>"
export GPG_PASSPHRASE="your-passphrase"
```

### Test APT signing:

```bash
# 1. Build repository (example - adjust for your project)
# ./scripts/release/build-apt-repo.sh

# 2. Sign repository
./scripts/release/sign-apt-repo.sh dist/deb-repo

# 3. Verify signatures created
ls -lh dist/deb-repo/dists/stable/
# Should see: Release, InRelease, Release.gpg

# 4. Verify signature is valid
gpg --verify dist/deb-repo/dists/stable/InRelease
# Should show: "Good signature from 'Release Manager...'"
```

### Test RPM signing:

```bash
# 1. Build RPM packages (example - adjust for your project)
# ./scripts/release/build-rpm.sh

# 2. Sign RPMs
./scripts/release/sign-rpm.sh dist/rpm

# 3. Verify signatures
rpm -qp --qf '%{SIGPGP:pgpsig}\n' dist/rpm/*.rpm
# Should show: "RSA/SHA256, ... Key ID ..."
```

---

## Step 5: Distribute Public Key

Users need your public key to verify packages.

### For APT Repository:

Add this to your project's README or documentation:

```bash
# Users run this to add your public key:
curl -fsSL https://yourdomain.com/apt-repo/keys/release-public-key.asc | sudo apt-key add -

# Or for Ubuntu 22.04+ (recommended):
curl -fsSL https://yourdomain.com/apt-repo/keys/release-public-key.asc | \
  sudo gpg --dearmor -o /usr/share/keyrings/redoubt-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/redoubt-archive-keyring.gpg] https://yourdomain.com/apt-repo stable main" | \
  sudo tee /etc/apt/sources.list.d/redoubt.list

sudo apt-get update
sudo apt-get install redoubt
```

### For RPM Repository:

Add this to your project's README or documentation:

```bash
# Users run this to add your public key:
sudo rpm --import https://yourdomain.com/rpm-repo/release-public-key.asc

# Add repository
sudo tee /etc/yum.repos.d/redoubt.repo <<EOF
[redoubt]
name=Redoubt Repository
baseurl=https://yourdomain.com/rpm-repo
enabled=1
gpgcheck=1
gpgkey=https://yourdomain.com/rpm-repo/release-public-key.asc
EOF

# Install
sudo dnf install redoubt  # Fedora/RHEL 8+
# or
sudo yum install redoubt  # CentOS 7/RHEL 7
```

---

## Troubleshooting

### "gpg: command not found"

```bash
# Install GPG:
# macOS
brew install gnupg

# Ubuntu/Debian
sudo apt-get install gnupg

# Fedora/RHEL
sudo dnf install gnupg2
```

### "gpg: signing failed: No secret key"

```bash
# List your keys to verify
gpg --list-secret-keys

# Verify GPG_KEY_NAME matches exactly
echo $GPG_KEY_NAME

# Re-import key if needed
cd gpg-keys
gpg --import release-private-key.asc
```

### "gpg: signing failed: Inappropriate ioctl for device"

```bash
# Set GPG_TTY environment variable
export GPG_TTY=$(tty)

# Add to your shell profile (~/.bashrc or ~/.zshrc):
echo 'export GPG_TTY=$(tty)' >> ~/.bashrc
```

### Workflow fails with "GPG error"

1. Check GitHub Secrets are set correctly
2. Verify `GPG_PRIVATE_KEY` is base64-encoded (from `.b64` file)
3. Verify `GPG_KEY_NAME` matches exactly (including spaces, parentheses, angle brackets)
4. Check `GPG_PASSPHRASE` doesn't have extra spaces or newlines

---

## Security Checklist

Before going to production:

- [ ] GPG key has a strong passphrase (minimum 20 characters)
- [ ] Private key files are NOT committed to git (check `.gitignore`)
- [ ] GitHub Secrets are set correctly
- [ ] Public key is published and accessible to users
- [ ] Signed test package locally and verified signature
- [ ] Tested signing in CI/CD pipeline
- [ ] Backed up private key to secure location (encrypted password manager)
- [ ] Documented key expiry date and rotation procedure
- [ ] Limited GitHub Actions permissions (least privilege)
- [ ] Monitored who has access to GitHub Secrets

---

## Next Steps

1. **Test in CI**: Push a tag and verify CI signing works
2. **Monitor expiry**: Set calendar reminder for key rotation (2 years)
3. **Document for users**: Add public key installation instructions to README
4. **Backup keys**: Store private key in encrypted vault
5. **Review regularly**: Audit who has access to GitHub Secrets

---

## Quick Reference

### Files Created:
```
scripts/ops/generate-gpg-key.sh        # Key generation script (run once)
scripts/release/setup-gpg-in-ci.sh     # CI setup (run in GitHub Actions)
scripts/release/sign-apt-repo.sh       # APT signing (existing)
scripts/release/sign-rpm.sh            # RPM signing (existing)
docs/security/GPG-KEY-MANAGEMENT.md    # Complete documentation
docs/security/QUICK-START-GPG.md       # This guide
```

### Environment Variables:
```bash
GPG_PRIVATE_KEY    # Base64-encoded private key (GitHub Secret)
GPG_KEY_NAME       # Key identifier (GitHub Secret)
GPG_PASSPHRASE     # Key passphrase (GitHub Secret)
GPG_TTY            # Terminal for GPG (local only)
```

### Commands:
```bash
# Generate key
./scripts/ops/generate-gpg-key.sh

# Setup in CI
./scripts/release/setup-gpg-in-ci.sh

# Sign APT
./scripts/release/sign-apt-repo.sh dist/deb-repo

# Sign RPM
./scripts/release/sign-rpm.sh dist/rpm

# Verify APT signature
gpg --verify dist/deb-repo/dists/stable/InRelease

# Verify RPM signature
rpm -qp --qf '%{SIGPGP:pggsig}\n' dist/rpm/*.rpm
```

---

**Need help?** See [GPG-KEY-MANAGEMENT.md](GPG-KEY-MANAGEMENT.md) for detailed documentation.

**Last Updated**: 2025-10-26
