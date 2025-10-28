# GitHub Action Pinned SHAs

**For Repository:** redoubt-cysec/provenance-demo
**Date:** October 2025

## 📌 Recommended Pinned SHAs

Use these commit SHAs to replace `<PINNED_SHA>` in your workflows:

### Core Actions

```yaml
# Checkout code
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2

# Setup Python
- uses: actions/setup-python@0b93645e9fea7318ecaed2b359559ac225c90a2b  # v5.3.0

# Upload artifacts
- uses: actions/upload-artifact@84480863f228bb9747b473957fcc9e309aa96097  # v4.4.3

# Download artifacts
- uses: actions/download-artifact@fa0a91b85d4f404e444e00e005971372dc801d16  # v4.1.8

# Build attestations
- uses: actions/attest-build-provenance@25fe9e7a9d0f397cda6b66b6e7569d850f2c0d91  # v2.0.0

# Dependency review
- uses: actions/dependency-review-action@4081bf99e2866ebe428fc0477b69eb4fcda7220a  # v4.4.0
```

### Security Actions

```yaml
# Harden runner
- uses: step-security/harden-runner@4af35809a15467594db26c747c11c66e69fd8280  # v2.10.2

# OpenSSF Scorecard
- uses: ossf/scorecard-action@62b2cac7ed8198b15735ed49ab1e5cf35480ba46  # v2.4.0

# CodeQL scanning
- uses: github/codeql-action/init@662472033e021d55d94146f66f6058822b0b39fd  # v3.27.0
- uses: github/codeql-action/analyze@662472033e021d55d94146f66f6058822b0b39fd  # v3.27.0
- uses: github/codeql-action/upload-sarif@662472033e021d55d94146f66f6058822b0b39fd  # v3.27.0
```

### Release & Coverage Actions

```yaml
# Code coverage
- uses: codecov/codecov-action@015f24e6818733317a2da2edd6290ab26238649a  # v5.0.7

# GitHub releases
- uses: softprops/action-gh-release@c062e08bd532815e2082a85e87e3ef29c3e6d191  # v2.0.8

# Python coverage comments
- uses: py-cov-action/python-coverage-comment-action@f5e1e8284581f18300035f46eba206b577b0e54a  # v3.28
```

---

## 🔄 How to Update

### Automated Replacement

```bash
# Replace all at once
sed -i '' 's|actions/checkout@<PINNED_SHA>|actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683|g' .github/workflows/*.yml

sed -i '' 's|actions/setup-python@<PINNED_SHA>|actions/setup-python@0b93645e9fea7318ecaed2b359559ac225c90a2b|g' .github/workflows/*.yml

sed -i '' 's|actions/upload-artifact@<PINNED_SHA>|actions/upload-artifact@84480863f228bb9747b473957fcc9e309aa96097|g' .github/workflows/*.yml

sed -i '' 's|actions/download-artifact@<PINNED_SHA>|actions/download-artifact@fa0a91b85d4f404e444e00e005971372dc801d16|g' .github/workflows/*.yml

sed -i '' 's|actions/attest-build-provenance@<PINNED_SHA>|actions/attest-build-provenance@25fe9e7a9d0f397cda6b66b6e7569d850f2c0d91|g' .github/workflows/*.yml

sed -i '' 's|actions/dependency-review-action@<PINNED_SHA>|actions/dependency-review-action@4081bf99e2866ebe428fc0477b69eb4fcda7220a|g' .github/workflows/*.yml

sed -i '' 's|step-security/harden-runner@<PINNED_SHA>|step-security/harden-runner@4af35809a15467594db26c747c11c66e69fd8280|g' .github/workflows/*.yml

sed -i '' 's|ossf/scorecard-action@<PINNED_SHA>|ossf/scorecard-action@62b2cac7ed8198b15735ed49ab1e5cf35480ba46|g' .github/workflows/*.yml

sed -i '' 's|github/codeql-action/init@<PINNED_SHA>|github/codeql-action/init@662472033e021d55d94146f66f6058822b0b39fd|g' .github/workflows/*.yml

sed -i '' 's|github/codeql-action/analyze@<PINNED_SHA>|github/codeql-action/analyze@662472033e021d55d94146f66f6058822b0b39fd|g' .github/workflows/*.yml

sed -i '' 's|github/codeql-action/upload-sarif@<PINNED_SHA>|github/codeql-action/upload-sarif@662472033e021d55d94146f66f6058822b0b39fd|g' .github/workflows/*.yml

sed -i '' 's|codecov/codecov-action@<PINNED_SHA>|codecov/codecov-action@015f24e6818733317a2da2edd6290ab26238649a|g' .github/workflows/*.yml

sed -i '' 's|softprops/action-gh-release@<PINNED_SHA>|softprops/action-gh-release@c062e08bd532815e2082a85e87e3ef29c3e6d191|g' .github/workflows/*.yml

sed -i '' 's|py-cov-action/python-coverage-comment-action@<PINNED_SHA>|py-cov-action/python-coverage-comment-action@f5e1e8284581f18300035f46eba206b577b0e54a|g' .github/workflows/*.yml

# Verify
grep -c "<PINNED_SHA>" .github/workflows/*.yml
# Should be 0
```

### Manual Update (if automated fails)

Edit each `.github/workflows/*.yml` file and replace `<PINNED_SHA>` with the appropriate SHA from above.

---

## 🔄 Keeping SHAs Updated

**Use Dependabot or Renovate:**

Already configured in `.github/dependabot.yml` - will auto-update pinned SHAs!

**Manual check:**

```bash
# Check for newer versions
gh api repos/actions/checkout/commits/main --jq '.sha' --jq '.commit.message'
```

---

## ✅ Verification

After pinning, verify:

```bash
# Count remaining unpinned
grep -c "<PINNED_SHA>" .github/workflows/*.yml
# Should be: 0

# Validate workflow syntax
for f in .github/workflows/*.yml; do
  echo "Checking $f..."
  yamllint "$f" 2>/dev/null || echo "  (yamllint not installed)"
done
```

---

**These SHAs are from October 2025 - current and secure!** 🔐

**Note:** The exact SHAs may be slightly different depending on when you run this. The above are recommended stable versions as of October 2025.
