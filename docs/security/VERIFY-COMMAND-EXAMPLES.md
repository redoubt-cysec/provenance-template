# Verify Command Examples

The `verify` command provides comprehensive security verification of your CLI binary with 14 different checks. This guide shows practical examples of using the enhanced verification features.

## Basic Usage

### Verify All Checks (Default)

```bash
provenance-demo verify
```

This runs all 14 verification checks on the current binary.

## New Features

### 1. Selective Check Execution

Run only specific checks instead of all 14:

```bash
# Run only checksum and signature verification
provenance-demo verify --checks checksum,signature

# Run SBOM-related checks
provenance-demo verify --checks sbom,sbom-attestation,osv

# Run attestation checks only
provenance-demo verify --checks attestation,slsa,build-env
```

**Available check keys:**
- `checksum` - SHA256 checksum verification
- `signature` - Sigstore signature verification
- `certificate` - Certificate identity validation
- `rekor` - Rekor transparency log verification
- `attestation` - GitHub attestation verification
- `sbom-attestation` - SBOM attestation verification
- `sbom` - SBOM format validation
- `osv` - OSV vulnerability scanning
- `slsa` - SLSA provenance verification
- `build-env` - Build environment verification
- `reproducible` - Reproducible build verification
- `metadata` - Artifact metadata verification
- `license` - License compliance checking
- `dependencies` - Dependency pinning verification

### 2. JSON Output for CI/CD Integration

Export verification results in JSON format:

```bash
# Output JSON to stdout
provenance-demo verify --json

# Save JSON report to file
provenance-demo verify --json --output verification-report.json
```

**JSON output structure:**
```json
{
  "binary": "/path/to/provenance-demo.pyz",
  "version": "0.1.0",
  "repository": "redoubt-cysec/provenance-template",
  "timestamp": "2025-11-01T20:00:00Z",
  "passed": true,
  "summary": {
    "total": 14,
    "passed": 14,
    "failed": 0
  },
  "checks": [
    {
      "check": "Checksum",
      "passed": true,
      "message": "SHA256 checksum matches release manifest",
      "details": "Checksum: 1234abcd... (manifest: checksums.txt)",
      "duration_ms": 15.32
    }
  ]
}
```

### 3. Verbose Mode with Timing

Show detailed output with execution timing for each check:

```bash
# Verbose mode
provenance-demo verify --verbose

# Short form
provenance-demo verify -v

# Combine with selective checks
provenance-demo verify -v --checks checksum,signature,attestation
```

**Verbose output shows timing:**
```
✓ Checksum: SHA256 checksum matches release manifest (15ms)
✓ Sigstore Signature: Signature verified via Rekor transparency log (1250ms)
✓ GitHub Attestation: GitHub attestation verified (890ms)
```

### 4. Save Reports to File

Save verification results to a file (JSON format):

```bash
# Save report in normal mode
provenance-demo verify --output verification-report.json

# Combine with JSON output
provenance-demo verify --json --output ci-report.json

# Combine with selective checks and verbose
provenance-demo verify -v --checks checksum,signature --output quick-check.json
```

### 5. Verify External Binary

Verify a specific binary file instead of the running one:

```bash
# Verify downloaded .pyz file
provenance-demo verify --file ./dist/provenance-demo.pyz

# With verbose mode
provenance-demo verify --file ./provenance-demo.pyz -v

# With JSON output
provenance-demo verify --file ./provenance-demo.pyz --json -o report.json
```

## CI/CD Integration Examples

### GitHub Actions

```yaml
- name: Verify Binary
  run: |
    ./provenance-demo.pyz verify --json --output verification-report.json

- name: Check Verification Status
  run: |
    if ! ./provenance-demo.pyz verify --checks checksum,signature,attestation; then
      echo "Critical security checks failed"
      exit 1
    fi

- name: Upload Verification Report
  uses: actions/upload-artifact@v4
  with:
    name: verification-report
    path: verification-report.json
```

### GitLab CI

```yaml
verify:
  script:
    - ./provenance-demo.pyz verify --json --output verification-report.json
    - cat verification-report.json
  artifacts:
    reports:
      junit: verification-report.json
    paths:
      - verification-report.json
```

### Jenkins Pipeline

```groovy
stage('Verify') {
    steps {
        sh './provenance-demo.pyz verify --json --output verification-report.json'
        archiveArtifacts artifacts: 'verification-report.json'

        script {
            def report = readJSON file: 'verification-report.json'
            if (!report.passed) {
                error("Verification failed: ${report.summary.failed} checks failed")
            }
        }
    }
}
```

## Quick Verification Workflows

### Fast Security Check (Critical Only)

Run only the most critical security checks:

```bash
provenance-demo verify --checks checksum,signature,attestation
```

This verifies:
- ✅ Binary hasn't been tampered with (checksum)
- ✅ Cryptographically signed (signature)
- ✅ Provenance attestation exists (attestation)

### Complete Supply Chain Audit

Run all security and compliance checks:

```bash
provenance-demo verify -v --output full-audit.json
```

This generates a complete audit report with all 14 checks and timing information.

### Vulnerability Check Only

Check for known vulnerabilities without running other checks:

```bash
provenance-demo verify --checks osv,sbom
```

This verifies:
- ✅ SBOM exists and is valid
- ✅ No known vulnerabilities in dependencies

## Programmatic Usage

### Parse JSON Output in Scripts

```bash
#!/bin/bash

# Run verification and capture JSON
./provenance-demo.pyz verify --json --output report.json

# Parse results with jq
PASSED=$(jq -r '.passed' report.json)
FAILED_COUNT=$(jq -r '.summary.failed' report.json)

if [ "$PASSED" != "true" ]; then
    echo "Verification failed: $FAILED_COUNT checks failed"

    # List failed checks
    jq -r '.checks[] | select(.passed == false) | "  - \(.check): \(.message)"' report.json

    exit 1
fi

echo "All checks passed!"
```

### Python Integration

```python
import subprocess
import json

# Run verification
result = subprocess.run(
    ['./provenance-demo.pyz', 'verify', '--json'],
    capture_output=True,
    text=True
)

# Parse JSON output
report = json.loads(result.stdout)

print(f"Verification: {'PASSED' if report['passed'] else 'FAILED'}")
print(f"Checks: {report['summary']['passed']}/{report['summary']['total']}")

# Check specific verifications
for check in report['checks']:
    if not check['passed']:
        print(f"  ✗ {check['check']}: {check['message']}")
```

## Performance Tips

1. **Quick checks first**: Use `--checks checksum,signature` for fast validation
2. **Skip expensive checks**: OSV scanning can be slow on large SBOMs
3. **Cache results**: Save JSON reports and reuse when binary hasn't changed
4. **Parallel CI jobs**: Run different check groups in parallel

```yaml
# GitHub Actions example
jobs:
  verify-critical:
    runs-on: ubuntu-latest
    steps:
      - run: ./binary verify --checks checksum,signature,attestation

  verify-compliance:
    runs-on: ubuntu-latest
    steps:
      - run: ./binary verify --checks license,dependencies

  verify-vulnerabilities:
    runs-on: ubuntu-latest
    steps:
      - run: ./binary verify --checks osv,sbom
```

## Troubleshooting

### Check Names Not Recognized

If you get "No valid checks found", list available checks:

```bash
# This will show available check keys
provenance-demo verify --checks invalid-check-name
```

### JSON Parsing Errors in CI

Ensure you're using `--json` flag for machine-readable output:

```bash
# Correct
./binary verify --json > report.json

# Incorrect (will include colored output)
./binary verify > report.json
```

### Missing Dependencies

Some checks require external tools:
- `signature`, `certificate`, `rekor`: Requires `cosign`
- `attestation`, `sbom-attestation`, `metadata`: Requires `gh` CLI
- `osv`: Requires `osv-scanner`

Install only what you need:

```bash
# For basic verification (checksum only)
./binary verify --checks checksum

# For signature verification (requires cosign)
brew install cosign
./binary verify --checks signature
```

## See Also

- [Verification Example](VERIFICATION-EXAMPLE.md) - Complete verification walkthrough
- [Supply Chain Security](SUPPLY-CHAIN.md) - Overall security architecture
- [Security Testing](SECURITY-TESTING.md) - Test coverage details
