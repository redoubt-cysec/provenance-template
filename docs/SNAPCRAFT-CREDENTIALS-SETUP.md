# Snapcraft Credentials Setup

This guide helps you export Snapcraft credentials for GitHub Actions automation.

## Problem: Keyring Error on Headless Systems

When running `snapcraft login` on VMs or headless systems, you may see:
```
No keyring found to store or retrieve credentials from.
```

## Solutions (Pick One)

### Option 1: Fix Keyring in VM (Recommended)

If you're in a Multipass or Ubuntu VM:

```bash
# Install keyring
sudo apt update
sudo apt install -y gnome-keyring dbus-x11

# Start keyring daemon
eval $(dbus-launch --sh-syntax)
eval $(echo "" | gnome-keyring-daemon --unlock)

# Now login works
snapcraft login
# Follow browser authentication

# Export credentials
snapcraft export-login snapcraft-credentials.txt
cat snapcraft-credentials.txt
```

### Option 2: Use Snapcraft Dashboard (Easiest)

1. Go to: https://dashboard.snapcraft.io/account/
2. Look for **"Export Login"** or **"Macaroon"** section
3. Download or copy the credentials
4. Add to GitHub:
   ```bash
   gh secret set SNAPCRAFT_STORE_CREDENTIALS \
     --repo redoubt-cysec/provenance-template \
     --body "PASTE_CREDENTIALS_HERE"
   ```

### Option 3: Complete Multipass Flow (macOS)

```bash
# On your Mac
multipass launch --name snapcred 22.04
multipass shell snapcred

# Inside VM
sudo apt update
sudo apt install -y snapcraft gnome-keyring dbus-x11

# Fix keyring
eval $(dbus-launch --sh-syntax)
eval $(echo "" | gnome-keyring-daemon --unlock)

# Login and export
snapcraft login
snapcraft export-login snapcraft-credentials.txt
cat snapcraft-credentials.txt
# Copy this output!

exit

# Back on Mac
multipass transfer snapcred:snapcraft-credentials.txt ./snapcraft-credentials.txt

# Add to GitHub
gh secret set SNAPCRAFT_STORE_CREDENTIALS < snapcraft-credentials.txt \
  --repo redoubt-cysec/provenance-template

# Verify
gh secret list --repo redoubt-cysec/provenance-template | grep SNAPCRAFT

# Clean up
rm snapcraft-credentials.txt
multipass delete snapcred
multipass purge
```

## Verify Setup

After adding the secret, verify it exists:

```bash
gh secret list --repo redoubt-cysec/provenance-template
```

You should see:
```
SNAPCRAFT_STORE_CREDENTIALS  Updated YYYY-MM-DD
```

## Test the Workflow

Trigger the snap publishing workflow manually:

1. Go to: https://github.com/redoubt-cysec/provenance-template/actions/workflows/snap-publish.yml
2. Click "Run workflow"
3. Enter version (e.g., `v0.1.0`) and channel (e.g., `edge`)
4. Watch it build and publish!

## Troubleshooting

### "No keyring found" Error

Install keyring and start daemon:
```bash
sudo apt install gnome-keyring dbus-x11
eval $(dbus-launch --sh-syntax)
eval $(echo "" | gnome-keyring-daemon --unlock)
```

### "Authentication failed" in GitHub Actions

- Verify secret is added: `gh secret list`
- Check credential format (should be base64 string)
- Re-export credentials if they expired

### Credentials Expired

Snapcraft credentials expire. If publishing fails:
1. Re-run `snapcraft login`
2. Re-export credentials
3. Update GitHub secret

## Security Notes

- ✅ Store credentials only in GitHub Secrets (encrypted)
- ✅ Delete local credential files after upload
- ✅ Never commit credentials to git
- ✅ Rotate credentials periodically (they expire automatically)
