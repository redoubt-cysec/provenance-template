# Badge Setup and Troubleshooting

This guide explains how to set up and troubleshoot the security badges in the README.

## Badge Overview

The template includes 8 badges that show project health and security status:

1. **Main Verify** - Status of main verification workflow
2. **Secure Release** - Status of secure release workflow
3. **OpenSSF Scorecard** - Security best practices score (0-10)
4. **Security Tests** - Status of security test suite
5. **Integration Tests** - Status of integration tests
6. **Codecov** - Code coverage percentage
7. **Python Version** - Supported Python versions
8. **License** - MIT license badge

## Common Issues and Solutions

### Issue 1: Secure Release Badge Shows "Failing"

**Symptom**: The Secure Release badge shows a red "failing" status even though workflows are passing.

**Cause**: The badge URL doesn't specify which branch to monitor, so it might show status from feature branches or PRs.

**Solution**: The badge URLs now include `?branch=main` parameter to explicitly show main branch status:

```markdown
[![Secure Release](https://github.com/owner/repo/actions/workflows/secure-release.yml/badge.svg?branch=main)](...)
```

**Verification**: Check that all GitHub Actions badges have `?branch=main` in their URLs.

### Issue 2: Codecov Badge Shows "Unknown"

**Symptom**: The Codecov badge displays "unknown" instead of a coverage percentage.

**Cause**: Codecov requires an upload token for repositories with protected branches. The coverage workflow was failing with:

```
error - Commit creating failed: {"message":"Token required - not valid tokenless upload"}
```

**Solution**: Add a Codecov token as a GitHub secret.

#### Step 1: Get Your Codecov Token

1. Go to [codecov.io](https://codecov.io) and sign in with GitHub
2. Add your repository (if not already added)
3. Navigate to your repository settings
4. Copy the "Repository Upload Token"

#### Step 2: Add Token to GitHub Secrets

1. Go to your GitHub repository settings
2. Navigate to **Settings → Secrets and variables → Actions**
3. Click **New repository secret**
4. Name: `CODECOV_TOKEN`
5. Value: Paste the token from Codecov
6. Click **Add secret**

#### Step 3: Verify Upload

After adding the token, the next workflow run should successfully upload coverage:

```bash
# Check coverage workflow status
gh run list --workflow=coverage.yml --limit 1

# View logs to verify upload succeeded
gh run view <run-id> --log | grep -A5 "Upload coverage"
```

Look for: `info - Process Upload complete`

#### Alternative: Public Repository Without Protected Branch

If your repository is public and the main branch is not protected, you can remove branch protection temporarily to allow tokenless uploads. However, using a token is recommended for security.

### Issue 3: OpenSSF Scorecard Score

**Current Score**: 5.7/10

**What This Means**: OpenSSF (Open Source Security Foundation) Scorecard evaluates your repository against security best practices. A score of 5.7 indicates moderate security posture with room for improvement.

#### Understanding the Score

The Scorecard checks multiple criteria including:
- Branch protection rules
- Dependency pinning
- Security policy (SECURITY.md)
- Signed releases
- Vulnerability disclosure
- CI/CD security
- Code review requirements
- And more...

#### How to Improve Your Score

1. **Check Your Current Score Details**:
   - Click the Scorecard badge in your README
   - Review which checks are passing/failing
   - Focus on the failing checks first

2. **Common Quick Wins**:

   **Enable Branch Protection** (if not already enabled):
   - Go to Settings → Branches → Add rule
   - Branch name pattern: `main`
   - Enable:
     - ✅ Require pull request before merging
     - ✅ Require approvals (at least 1)
     - ✅ Require status checks to pass
     - ✅ Require conversation resolution
     - ✅ Include administrators

   **Add Security Policy**:
   - Create `SECURITY.md` in repository root
   - Include vulnerability reporting instructions
   - Reference: [GitHub Security Policy Guide](https://docs.github.com/en/code-security/getting-started/adding-a-security-policy-to-your-repository)

   **Enable Dependabot**:
   - Go to Settings → Security & analysis
   - Enable "Dependency graph"
   - Enable "Dependabot alerts"
   - Enable "Dependabot security updates"

   **Pin GitHub Actions** (already done in this template):
   - All actions should be pinned to commit SHAs
   - Example: `actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683`

3. **Check Score After Changes**:
   - Scorecard updates daily
   - Changes may take 24-48 hours to reflect
   - Monitor progress via the badge

#### Target Scores

- **5.0-6.0**: Basic security practices ← **Current**
- **6.0-7.0**: Good security posture
- **7.0-8.0**: Strong security practices
- **8.0-9.0**: Excellent security posture
- **9.0-10.0**: Best-in-class security

## Badge URL Reference

### GitHub Actions Badges

Pattern for workflow badges:
```
https://github.com/{owner}/{repo}/actions/workflows/{workflow}.yml/badge.svg?branch=main
```

Always include `?branch=main` to show main branch status only.

### Codecov Badge

```
https://codecov.io/gh/{owner}/{repo}/branch/main/graph/badge.svg
```

The `/branch/main` path ensures the badge shows main branch coverage.

### OpenSSF Scorecard Badge

```
https://api.scorecard.dev/projects/github.com/{owner}/{repo}/badge
```

This badge updates automatically (daily) based on repository analysis.

## Troubleshooting Tips

### Badges Not Updating

**Symptom**: Badge still shows old status after fixes.

**Solutions**:
1. **Browser Cache**: Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
2. **CDN Cache**: Badge CDNs cache for 5-10 minutes
3. **Query Parameter**: Add `?branch=main&event=push` to force refresh
4. **Direct Check**: Click the badge to view actual workflow/service status

### Codecov Upload Still Failing

Check the workflow logs:

```bash
# View latest coverage workflow run
gh run view $(gh run list --workflow=coverage.yml --limit 1 --json databaseId --jq '.[0].databaseId') --log

# Look for specific errors
gh run view <run-id> --log | grep -i "error"
```

Common errors:
- `Token required`: Add `CODECOV_TOKEN` secret
- `Invalid token`: Regenerate token in Codecov
- `File not found`: Check `files: ./coverage.xml` path

### OpenSSF Scorecard Not Improving

After making changes:
1. Wait 24-48 hours for re-scan
2. Verify changes are on main branch
3. Check Scorecard action logs (if running it via workflow)
4. Visit scorecard.dev directly to see detailed results

## Testing Badge URLs

You can test badge URLs directly:

```bash
# Test GitHub Actions badge
curl -I "https://github.com/redoubt-cysec/provenance-template/actions/workflows/secure-release.yml/badge.svg?branch=main"

# Test Codecov badge
curl -I "https://codecov.io/gh/redoubt-cysec/provenance-template/branch/main/graph/badge.svg"

# Test OpenSSF Scorecard badge
curl -I "https://api.scorecard.dev/projects/github.com/redoubt-cysec/provenance-template/badge"
```

All should return `HTTP/2 200` status.

## Next Steps

After setting up all badges:

1. **Verify Badge Display**: Check README renders correctly on GitHub
2. **Test Badge Links**: Click each badge to ensure it links to correct page
3. **Monitor Status**: Set up notifications for workflow failures
4. **Improve Scores**: Work on improving Codecov percentage and OpenSSF score
5. **Document Progress**: Update README with badge explanations if needed

## See Also

- [Supply Chain Security](SUPPLY-CHAIN.md) - Overall security architecture
- [Security Testing](SECURITY-TESTING.md) - Test coverage details
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Codecov Documentation](https://docs.codecov.com/)
- [OpenSSF Scorecard](https://github.com/ossf/scorecard)
