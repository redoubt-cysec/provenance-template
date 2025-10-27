# GPG Key Management

## Overview

GPG signing is **required** for production release to:

- Sign APT repository metadata (`Release`, `InRelease`, `Release.gpg`)
- Sign RPM packages (`.rpm` files)
- Verify package authenticity for end users

This guide covers:

1. Generating GPG keys locally
2. Exporting keys for CI/CD
3. Setting up keys in GitHub Actions
4. Testing signature verification
5. Key rotation procedures

---

## 1. Generate GPG Key (Local/Offline)

### Quick Start (Automated)

Use the provided script for interactive key generation:

```bash
./scripts/ops/generate-gpg-key.sh
```

This script will:

- ✅ Generate 4096-bit RSA keypair
- ✅ Prompt for name, email, validity, passphrase
- ✅ Export public key, private key, and base64-encoded private key
- ✅ Generate key fingerprint
- ✅ Provide setup instructions for GitHub Secrets

**Output files** (in `gpg-keys/`):

- `release-public-key.asc` - Public key (distribute to users)
- `release-private-key.asc` - Private key (NEVER commit to git)
- `release-private-key.b64` - Base64-encoded private key (for GitHub Secrets)
- `key-fingerprint.txt` - Key fingerprint

### Manual Generation

If you prefer manual generation:

```bash
cat > gen.cfg <<'EOF'
Key-Type: RSA
Key-Length: 4096
Subkey-Type: RSA
Subkey-Length: 4096
Name-Real: Release Manager
Name-Comment: redoubt Release Key
Name-Email: noreply@example.com
Expire-Date: 2y
Passphrase: YOUR_SECURE_PASSPHRASE
%commit
%echo GPG key generated successfully
EOF

gpg --batch --generate-key gen.cfg
```

**Note**: Use a strong passphrase for production keys!

---

## 2. Export Keys for CI/CD

### Export Private Key

```bash
# Set key identifier
KEY_NAME="Release Manager (redoubt Release Key) <noreply@example.com>"

# Export armored private key
gpg --armor --export-secret-keys "$KEY_NAME" > release-private-key.asc

# Export as base64 (for GitHub Secrets)
base64 < release-private-key.asc > release-private-key.b64
```

### Export Public Key

```bash
# Export armored public key
gpg --armor --export "$KEY_NAME" > release-public-key.asc
```

### Get Key Fingerprint

```bash
# Get fingerprint (for verification)
gpg --fingerprint "$KEY_NAME" | grep "Key fingerprint"
```

---

## 3. GitHub Actions Setup

### Add GitHub Secrets

Go to: `https://github.com/OWNER/REPO/settings/secrets/actions`

Add these secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `GPG_PRIVATE_KEY` | Contents of `release-private-key.b64` | Base64-encoded private key |
| `GPG_KEY_NAME` | `Release Manager (redoubt Release Key) <noreply@example.com>` | Key identifier (uid) |
| `GPG_PASSPHRASE` | Your passphrase | ⚠️ Required if key has passphrase |

### Use in Workflow

Add to your GitHub Actions workflow:

```yaml
jobs:
  sign-packages:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup GPG
        env:
          GPG_PRIVATE_KEY: ${{ secrets.GPG_PRIVATE_KEY }}
          GPG_KEY_NAME: ${{ secrets.GPG_KEY_NAME }}
          GPG_PASSPHRASE: ${{ secrets.GPG_PASSPHRASE }}
        run: |
          ./scripts/release/setup-gpg-in-ci.sh

      - name: Build APT repository
        run: |
          # Your build steps here
          ./scripts/release/build-apt-repo.sh

      - name: Sign APT repository
        env:
          GPG_KEY_NAME: ${{ secrets.GPG_KEY_NAME }}
          GPG_PASSPHRASE: ${{ secrets.GPG_PASSPHRASE }}
        run: |
          ./scripts/release/sign-apt-repo.sh dist/deb-repo

      - name: Build RPM packages
        run: |
          # Your build steps here
          ./scripts/release/build-rpm.sh

      - name: Sign RPM packages
        env:
          GPG_KEY_NAME: ${{ secrets.GPG_KEY_NAME }}
          GPG_PASSPHRASE: ${{ secrets.GPG_PASSPHRASE }}
        run: |
          ./scripts/release/sign-rpm.sh dist/rpm
```

---

## 4. Distributing Public Key

### APT Repository

Users need the public key to verify packages:

**Option 1: Direct download**

```bash
# Users run:
curl -fsSL https://yourdomain.com/apt-repo/keys/release-public-key.asc | sudo apt-key add -
```

**Option 2: Use signed-by (recommended for Ubuntu 22.04+)**

```bash
# Users run:
curl -fsSL https://yourdomain.com/apt-repo/keys/release-public-key.asc | \
  sudo gpg --dearmor -o /usr/share/keyrings/redoubt-archive-keyring.gpg

# In sources.list:
deb [signed-by=/usr/share/keyrings/redoubt-archive-keyring.gpg] https://yourdomain.com/apt-repo stable main
```

### RPM Repository

Users need the public key to verify packages:

```bash
# Users run:
sudo rpm --import https://yourdomain.com/rpm-repo/release-public-key.asc
```

### GitHub Releases

Attach the public key to your GitHub releases so users can download it:

```bash
# In release workflow:
gh release upload v1.0.0 gpg-keys/release-public-key.asc
```

---

## 5. Testing Signatures

### Test APT Signing Locally

```bash
# Set environment variables
export GPG_KEY_NAME="Release Manager (redoubt Release Key) <noreply@example.com>"
export GPG_PASSPHRASE="your_passphrase"  # If key has passphrase

# Build repository (example)
# ./scripts/release/build-apt-repo.sh

# Sign repository
./scripts/release/sign-apt-repo.sh dist/deb-repo

# Verify signatures were created
ls -lh dist/deb-repo/dists/stable/
# Should see: Release, InRelease, Release.gpg

# Verify signature
gpg --verify dist/deb-repo/dists/stable/InRelease
```

### Test RPM Signing Locally

```bash
# Set environment variables
export GPG_KEY_NAME="Release Manager (redoubt Release Key) <noreply@example.com>"
export GPG_PASSPHRASE="your_passphrase"  # If key has passphrase

# Build RPM packages (example)
# ./scripts/release/build-rpm.sh

# Sign RPMs
./scripts/release/sign-rpm.sh dist/rpm

# Verify signature
rpm -qp --qf '%{SIGPGP:pgpsig}\n' dist/rpm/*.rpm
# Should show "RSA/SHA256" signature
```

### Test in VM

The Phase 2 VM tests now include signature verification:

```bash
# Test APT repository with signature verification
./scripts/phase2-testing/test-apt-repo-vm.sh

# Test RPM repository with signature verification
./scripts/phase2-testing/test-rpm-repo-vm.sh
```

---

## 6. Key Rotation

### When to Rotate

- Key expiring soon (< 30 days)
- Key compromised or suspected compromise
- Regular rotation policy (recommended: every 2 years)
- Team member with key access leaves

### Rotation Procedure

**Phase 1: Generate New Key (Week 1)**

```bash
# Generate new key with updated expiry
./scripts/ops/generate-gpg-key.sh

# Export both public keys
gpg --armor --export "OLD_KEY_NAME" > old-public-key.asc
gpg --armor --export "NEW_KEY_NAME" > new-public-key.asc
```

**Phase 2: Dual Signing (Weeks 2-4)**

```bash
# Update CI secrets with new key
# But keep old key available

# Sign repos with BOTH keys for 2-4 weeks
./scripts/release/sign-apt-repo.sh --key-name "$OLD_KEY_NAME"
./scripts/release/sign-apt-repo.sh --key-name "$NEW_KEY_NAME"

# Publish both public keys
```

**Phase 3: Deprecation Notice (Week 4)**

```bash
# Announce old key deprecation
# Give users 2-4 weeks to update their systems
```

**Phase 4: Remove Old Key (Week 6-8)**

```bash
# Stop signing with old key
# Remove old public key from distribution
# Revoke old key if compromised

# Revoke old key (if needed)
gpg --gen-revoke "$OLD_KEY_NAME" > revocation-cert.asc
```

### Maintain Overlapping Validity

- New key should be created before old key expires
- Overlap period: minimum 2 weeks, recommended 4-8 weeks
- Dual-sign all releases during overlap
- Announce rotation to users via:
  - GitHub releases
  - Documentation updates
  - Email notifications (if applicable)

---

## 7. Security Best Practices

### Key Storage

- ✅ **DO**: Store private keys in encrypted password manager
- ✅ **DO**: Use strong passphrases (minimum 20 characters)
- ✅ **DO**: Store base64-encoded keys as GitHub Secrets
- ✅ **DO**: Backup keys to encrypted offline storage
- ❌ **DO NOT**: Commit private keys to git
- ❌ **DO NOT**: Share private keys via email/Slack
- ❌ **DO NOT**: Use keys without passphrase in production

### Key Usage

- ✅ **DO**: Use dedicated keys for package signing
- ✅ **DO**: Rotate keys every 1-2 years
- ✅ **DO**: Monitor key expiry dates
- ✅ **DO**: Test signature verification regularly
- ❌ **DO NOT**: Use personal GPG keys for package signing
- ❌ **DO NOT**: Share keys between projects
- ❌ **DO NOT**: Use keys without expiry date

### CI/CD Security

- ✅ **DO**: Use GitHub Secrets for private keys
- ✅ **DO**: Limit GitHub Actions permissions
- ✅ **DO**: Use environment-specific secrets
- ✅ **DO**: Audit who has access to secrets
- ❌ **DO NOT**: Print private keys in logs
- ❌ **DO NOT**: Export keys to workflow artifacts
- ❌ **DO NOT**: Use secrets in pull requests from forks

---

## 8. Troubleshooting

### "gpg: signing failed: No secret key"

```bash
# List available keys
gpg --list-secret-keys

# Verify key name matches
echo $GPG_KEY_NAME

# Re-import key if needed
echo "$GPG_PRIVATE_KEY" | base64 --decode | gpg --batch --yes --import
```

### "gpg: signing failed: Inappropriate ioctl for device"

```bash
# Set GPG_TTY
export GPG_TTY=$(tty)

# Or use loopback pinentry mode
echo "pinentry-mode loopback" >> ~/.gnupg/gpg.conf
```

### "gpg: public key decryption failed: Bad passphrase"

```bash
# Verify passphrase is correct
# Check for extra spaces/newlines

# Test passphrase manually
echo "test" | gpg --batch --passphrase "$GPG_PASSPHRASE" \
  --pinentry-mode loopback --local-user "$GPG_KEY_NAME" --clearsign
```

### "E: GPG error: Release is not signed"

```bash
# Verify signature files exist
ls -lh dist/deb-repo/dists/stable/
# Should have: InRelease, Release, Release.gpg

# Verify signature is valid
gpg --verify dist/deb-repo/dists/stable/InRelease
```

---

## 9. References

- **GPG Documentation**: <https://gnupg.org/documentation/>
- **Debian Repository Format**: <https://wiki.debian.org/DebianRepository/Format>
- **RPM Signing**: <https://rpm-software-management.github.io/rpm/manual/signatures.html>
- **GitHub Actions Encrypted Secrets**: <https://docs.github.com/en/actions/security-guides/encrypted-secrets>

---

**Last Updated**: 2025-10-26
**Script Version**: 1.0.0
**Minimum GPG Version**: 2.2.0
