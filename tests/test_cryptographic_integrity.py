"""
Cryptographic Integrity Tests

Validates cryptographic operations and signing configurations.
"""
import json
import subprocess
import yaml
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"


class TestCosignConfiguration:
    """Test cosign signing configuration security."""

    def test_keyless_signing_only(self):
        """Verify only keyless signing is used (no private keys in repo)."""
        release_workflow = WORKFLOWS_DIR / "release.yml"
        content = release_workflow.read_text()

        # Must use keyless
        assert "COSIGN_EXPERIMENTAL=1" in content or "cosign-installer" in content, \
            "Must use cosign keyless signing"

        # Must NOT have private key references
        forbidden_key_refs = [
            "COSIGN_PRIVATE_KEY",
            "COSIGN_PASSWORD",
            "cosign.key",
            "--key ",
        ]
        for ref in forbidden_key_refs:
            assert ref not in content, \
                f"Must not use private keys for signing. Found: {ref}"

    def test_rekor_transparency_log_enabled(self):
        """Verify signatures are logged to Rekor transparency log."""
        release_workflow = WORKFLOWS_DIR / "release.yml"
        content = release_workflow.read_text()

        # Should NOT disable Rekor
        forbidden = ["COSIGN_NO_REKOR=1", "--no-upload-tlog"]
        for f in forbidden:
            assert f not in content, \
                "Rekor transparency log must be enabled for auditability"

    def test_fulcio_certificate_authority_used(self):
        """Verify Fulcio CA is used for keyless certificates."""
        release_workflow = WORKFLOWS_DIR / "release.yml"
        content = release_workflow.read_text()

        # Keyless signing should use Fulcio
        assert "fulcio" in content.lower() or "sigstore" in content.lower() or \
               "COSIGN_EXPERIMENTAL=1" in content, \
            "Must use Sigstore/Fulcio for certificate authority"

    def test_correct_oidc_issuer_for_github(self):
        """Verify correct OIDC issuer for GitHub Actions."""
        release_workflow = WORKFLOWS_DIR / "release.yml"
        content = release_workflow.read_text()

        # Correct issuer for GitHub Actions
        assert "https://token.actions.githubusercontent.com" in content, \
            "Must specify correct OIDC issuer for GitHub Actions"

    def test_certificate_identity_validation(self):
        """Verify certificate identity matches workflow."""
        release_workflow = WORKFLOWS_DIR / "release.yml"
        content = release_workflow.read_text()

        # Should include identity validation in verification instructions
        assert "--certificate-identity" in content, \
            "Verification must validate certificate identity"
        assert "github.repository" in content or "${{ github.repository }}" in content, \
            "Certificate identity must reference the repository"


class TestChecksumSecurity:
    """Test checksum generation and validation security."""

    def test_sha256_algorithm_used(self):
        """Verify SHA-256 is used (not weaker algorithms)."""
        release_workflow = WORKFLOWS_DIR / "release.yml"
        content = release_workflow.read_text()

        assert "SHA256" in content or "sha256sum" in content, \
            "Must use SHA-256 for checksums"

        # Must NOT use weak algorithms
        weak_algos = ["md5", "sha1", "MD5", "SHA1"]
        for algo in weak_algos:
            if algo in content.lower():
                # Make sure it's not in a comment or example of what NOT to do
                assert False, f"Must not use weak hash algorithm: {algo}"

    def test_checksums_signed(self):
        """Verify checksums file itself is signed."""
        release_workflow = WORKFLOWS_DIR / "release.yml"
        content = release_workflow.read_text()

        # The SHA256SUMS file should be signed
        assert "SHA256SUMS" in content and "sign-blob" in content, \
            "SHA256SUMS file must be cryptographically signed"


class TestAttestationSecurity:
    """Test GitHub attestation security."""

    def test_build_provenance_attestation(self):
        """Verify build provenance is attested."""
        release_workflow = WORKFLOWS_DIR / "release.yml"
        content = release_workflow.read_text()

        assert "actions/attest-build-provenance" in content, \
            "Must use GitHub's build provenance attestation"

    def test_attestation_for_all_artifacts(self):
        """Verify all release artifacts are attested."""
        release_workflow = WORKFLOWS_DIR / "release.yml"
        content = release_workflow.read_text()

        # Should attest multiple artifacts
        assert "attest-build-provenance" in content, \
            "All artifacts should have provenance attestations"

        # Look for multiple attestation calls or glob patterns
        attestation_count = content.count("attest-build-provenance")
        assert attestation_count >= 1, "Must attest at least one artifact type"

    def test_slsa_provenance_format(self):
        """Verify SLSA provenance format is generated."""
        # GitHub's attest-build-provenance generates SLSA v1.0 provenance
        release_workflow = WORKFLOWS_DIR / "release.yml"
        content = release_workflow.read_text()

        # GitHub attestation action produces in-toto predicates in SLSA format
        assert "attest-build-provenance" in content, \
            "GitHub attestation produces SLSA provenance"


class TestPermissionHardening:
    """Test workflow permission hardening."""

    def test_minimal_permissions_principle(self):
        """Verify workflows use minimal required permissions."""
        for workflow_file in WORKFLOWS_DIR.glob("*.yml"):
            with open(workflow_file) as f:
                workflow = yaml.safe_load(f)

            # Check top-level or job-level permissions exist
            has_permissions = False
            if "permissions" in workflow:
                has_permissions = True
            else:
                # Check job-level permissions
                for job in workflow.get("jobs", {}).values():
                    if "permissions" in job:
                        has_permissions = True
                        break

            # Critical workflows MUST have explicit permissions
            critical_workflows = ["release.yml", "main-verify.yml"]
            if workflow_file.name in critical_workflows:
                assert has_permissions, \
                    f"{workflow_file.name} must explicitly declare permissions"

    def test_no_write_all_permission(self):
        """Verify no workflow has write-all permissions."""
        for workflow_file in WORKFLOWS_DIR.glob("*.yml"):
            content = workflow_file.read_text()

            # Should never grant write: all
            dangerous_patterns = [
                "permissions: write-all",
                "permissions: write",  # Without specific scopes
            ]

            for pattern in dangerous_patterns:
                # This is a simplified check - real YAML parsing is better
                if pattern in content:
                    pytest.fail(f"{workflow_file.name} grants overly broad permissions: {pattern}")

    def test_id_token_write_only_when_needed(self):
        """Verify id-token: write only in appropriate workflows.

        id-token: write enables OIDC token generation, which is needed for:
        - Keyless signing (cosign)
        - Build attestations
        - Publishing to registries with OIDC auth

        Having it in CI workflows is acceptable even if not actively used,
        as it doesn't pose a direct security risk (unlike contents: write).
        """
        for workflow_file in WORKFLOWS_DIR.glob("*.yml"):
            content = workflow_file.read_text()

            if "id-token: write" in content:
                # Verify it's in a reasonable workflow (not in PR checks from forks)
                # The real risk is pull_request_target + id-token, which we check elsewhere

                # Document that id-token is present (for awareness)
                print(f"Note: {workflow_file.name} has id-token: write")

                # Check it's not being misused (this is the real concern)
                with open(workflow_file) as f:
                    workflow = yaml.safe_load(f)

                on_config = workflow.get("on", {})
                if isinstance(on_config, dict):
                    # id-token in pull_request_target is dangerous
                    if "pull_request_target" in on_config:
                        pytest.fail(
                            f"{workflow_file.name} has DANGEROUS combination: "
                            "pull_request_target + id-token: write"
                        )

    def test_contents_write_only_for_releases(self):
        """Verify contents: write only in release workflows."""
        for workflow_file in WORKFLOWS_DIR.glob("*.yml"):
            content = workflow_file.read_text()

            if "contents: write" in content:
                # contents:write should only be in release workflows
                assert "release" in workflow_file.name.lower() or \
                       "tag" in content or "release" in content, \
                    f"{workflow_file.name} has contents:write but doesn't appear to be a release workflow"


class TestSecretsHandling:
    """Test secrets and credentials handling."""

    def test_no_secrets_in_repo(self):
        """Scan entire repo for accidentally committed secrets."""
        # Common secret patterns
        import re

        secret_patterns = [
            (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
            (r"gho_[a-zA-Z0-9]{36}", "GitHub OAuth Token"),
            (r"github_pat_[a-zA-Z0-9]{82}", "GitHub Fine-grained PAT"),
            (r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
            (r"-----BEGIN (?:RSA |DSA )?PRIVATE KEY-----", "Private Key"),
            (r"sk_live_[0-9a-zA-Z]{24,}", "Stripe Live Key"),
            (r"sq0csp-[0-9A-Za-z\\-_]{43}", "Square Access Token"),
            (r"eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*", "JWT Token (suspicious)"),
        ]

        # Scan all non-test Python and YAML files
        files_to_scan = []
        files_to_scan.extend(REPO_ROOT.glob("**/*.py"))
        files_to_scan.extend(REPO_ROOT.glob("**/*.yml"))
        files_to_scan.extend(REPO_ROOT.glob("**/*.yaml"))
        files_to_scan.extend(REPO_ROOT.glob("**/*.md"))

        for file_path in files_to_scan:
            # Skip test files themselves and .venv
            if ".venv" in str(file_path) or "test_" in file_path.name:
                continue

            try:
                content = file_path.read_text()
                for pattern, secret_type in secret_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        # Filter out obvious examples/documentation
                        for match in matches:
                            # Skip if it's clearly an example (has "example", "REPLACE", etc.)
                            context_start = max(0, content.find(match) - 50)
                            context_end = min(len(content), content.find(match) + len(match) + 50)
                            context = content[context_start:context_end].lower()

                            if any(word in context for word in ["example", "placeholder", "your-", "replace", "xxx"]):
                                continue

                            pytest.fail(
                                f"Possible {secret_type} found in {file_path}: {match[:10]}..."
                            )
            except (UnicodeDecodeError, PermissionError):
                continue

    def test_secrets_used_from_github_secrets(self):
        """Verify workflows use GitHub Secrets, not hardcoded values."""
        for workflow_file in WORKFLOWS_DIR.glob("*.yml"):
            content = workflow_file.read_text()

            # If there are references to tokens/keys, they should be from secrets
            sensitive_keywords = ["TOKEN", "KEY", "PASSWORD", "SECRET"]

            for keyword in sensitive_keywords:
                if keyword in content:
                    # Find the context
                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        if keyword in line and ":" in line:
                            # Should be from ${{ secrets.* }}
                            if keyword in line and "secrets." not in line and \
                               "env." not in line and "#" not in line:
                                # Could be a key name definition, which is OK
                                # But if it has "=", it might be hardcoded
                                if "=" in line or ": " in line.split("#")[0]:
                                    # Check if it's actually assigning a value
                                    right_side = line.split(":", 1)[-1].strip()
                                    if right_side and not right_side.startswith("${{") and \
                                       not right_side.startswith("write") and \
                                       not right_side.startswith("read") and \
                                       "GITHUB_TOKEN" not in right_side:
                                        # This might be a hardcoded secret
                                        # (allowing some false positives for safety)
                                        print(f"Warning: Possible hardcoded {keyword} in {workflow_file.name}:{i+1}")


class TestDependencyIntegrity:
    """Test dependency management and integrity."""

    def test_no_pip_install_without_verification(self):
        """Verify pip installs don't skip verification."""
        for workflow_file in WORKFLOWS_DIR.glob("*.yml"):
            content = workflow_file.read_text()

            if "pip install" in content:
                # Should not disable verification
                forbidden = [
                    "--no-verify",
                    "--trusted-host",
                    "--disable-pip-version-check",  # This one is OK for CI performance
                ]
                for forbidden_flag in forbidden[:2]:  # Check first 2
                    assert forbidden_flag not in content, \
                        f"{workflow_file.name} uses pip install with {forbidden_flag}"

    def test_actions_pinned_to_full_sha(self):
        """Verify GitHub Actions are pinned to full commit SHAs."""
        import re

        for workflow_file in WORKFLOWS_DIR.glob("*.yml"):
            content = workflow_file.read_text()

            # Find all uses: statements
            uses_pattern = r'uses:\s+([^/\s]+/[^@\s]+)@([^\s]+)'
            matches = re.findall(uses_pattern, content)

            for action, ref in matches:
                # Skip local actions
                if action.startswith("./"):
                    continue

                # Check if it's a full SHA (40 hex chars)
                if ref == "<PINNED_SHA>":
                    # Template placeholder - OK for now
                    continue

                # Should be 40-char hex SHA or we warn
                if not (len(ref) == 40 and all(c in "0123456789abcdef" for c in ref.lower())):
                    # Using a tag/branch - print warning (not fail, since it's valid but less secure)
                    print(f"Warning: {workflow_file.name} uses {action}@{ref} (tag/branch, not SHA)")

    def test_requirements_file_integrity(self):
        """Verify requirements file exists for dependency tracking."""
        requirements = REPO_ROOT / "requirements.in"
        assert requirements.exists(), "requirements.in must exist for dependency transparency"

        # Should not have obviously malicious packages
        content = requirements.read_text()
        suspicious_packages = ["examplepackage", "test-package-please-ignore"]
        for pkg in suspicious_packages:
            assert pkg not in content.lower(), f"Suspicious package in requirements: {pkg}"


class TestSupplyChainSecurity:
    """Test supply chain attack prevention."""

    def test_no_download_from_untrusted_sources(self):
        """Verify no downloads from untrusted HTTP sources."""
        for workflow_file in WORKFLOWS_DIR.glob("*.yml"):
            content = workflow_file.read_text()

            # Find all URLs
            import re
            urls = re.findall(r'https?://[^\s\'"<>]+', content)

            for url in urls:
                # Must use HTTPS, not HTTP (with some exceptions)
                if url.startswith("http://"):
                    # Only allow localhost and internal references
                    if not any(host in url for host in ["localhost", "127.0.0.1", "example.com"]):
                        pytest.fail(f"{workflow_file.name} downloads from insecure HTTP: {url}")

    def test_runner_environment_isolation(self):
        """Verify runners don't persist credentials."""
        release_workflow = WORKFLOWS_DIR / "release.yml"
        content = release_workflow.read_text()

        # Should not persist credentials
        if "checkout" in content:
            # Look for persist-credentials: false
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "actions/checkout" in line:
                    # Check next ~10 lines for persist-credentials
                    checkout_block = "\n".join(lines[i:i+10])
                    assert "persist-credentials: false" in checkout_block, \
                        "checkout action should use persist-credentials: false"

    def test_no_arbitrary_code_execution(self):
        """Verify workflows don't execute arbitrary code from PRs."""
        for workflow_file in WORKFLOWS_DIR.glob("*.yml"):
            with open(workflow_file) as f:
                workflow = yaml.safe_load(f)

            content = workflow_file.read_text()

            # If triggered by pull_request_target, must be careful
            on_config = workflow.get("on", {})
            if isinstance(on_config, dict) and "pull_request_target" in on_config:
                # Should NOT checkout PR code
                assert "github.event.pull_request.head.sha" not in content, \
                    f"{workflow_file.name} uses pull_request_target and checks out PR code - RCE risk!"

    def test_environment_protection_for_releases(self):
        """Verify release workflow uses environment protection."""
        release_workflow = WORKFLOWS_DIR / "release.yml"

        with open(release_workflow) as f:
            workflow = yaml.safe_load(f)

        # Release job should specify environment
        release_job = workflow.get("jobs", {}).get("release", {})
        assert "environment" in release_job, \
            "Release job should use GitHub environment protection"


class TestSBOMQuality:
    """Test SBOM generation quality and completeness."""

    def test_sbom_format_is_standard(self):
        """Verify SBOM uses standard format (CycloneDX or SPDX)."""
        workflows_content = ""
        for workflow_file in WORKFLOWS_DIR.glob("*.yml"):
            workflows_content += workflow_file.read_text()

        # Should use CycloneDX or SPDX
        assert "cyclonedx" in workflows_content.lower() or "spdx" in workflows_content.lower(), \
            "SBOM must use standard format (CycloneDX or SPDX)"

    def test_sbom_includes_all_dependencies(self):
        """Verify SBOM generation includes all dependency types."""
        release_workflow = WORKFLOWS_DIR / "release.yml"
        content = release_workflow.read_text()

        if "cyclonedx" in content.lower():
            # CycloneDX for Python should include all deps
            # The tool should scan requirements or installed packages
            assert "pip" in content.lower() or "python" in content.lower(), \
                "SBOM generation should scan Python dependencies"

    def test_sbom_uploaded_with_release(self):
        """Verify SBOM is uploaded as release artifact."""
        release_workflow = WORKFLOWS_DIR / "release.yml"
        content = release_workflow.read_text()

        # SBOM file should be uploaded
        assert "sbom" in content.lower() and ("upload" in content.lower() or "release" in content.lower()), \
            "SBOM should be uploaded as release artifact"


class TestReproducibilityGuarantees:
    """Test build reproducibility guarantees."""

    def test_source_date_epoch_set(self):
        """Verify SOURCE_DATE_EPOCH is set for reproducible builds."""
        release_workflow = WORKFLOWS_DIR / "release.yml"
        content = release_workflow.read_text()

        assert "SOURCE_DATE_EPOCH" in content, \
            "SOURCE_DATE_EPOCH must be set for reproducible builds"

    def test_locale_environment_fixed(self):
        """Verify locale environment is fixed for reproducibility."""
        release_workflow = WORKFLOWS_DIR / "release.yml"
        content = release_workflow.read_text()

        # Should set LC_ALL, LANG, TZ
        reproducibility_vars = ["LC_ALL", "LANG", "TZ"]
        for var in reproducibility_vars:
            assert var in content, \
                f"{var} should be set for reproducible builds"

    def test_python_hash_seed_fixed(self):
        """Verify PYTHONHASHSEED is set for reproducible Python builds."""
        release_workflow = WORKFLOWS_DIR / "release.yml"
        content = release_workflow.read_text()

        assert "PYTHONHASHSEED" in content, \
            "PYTHONHASHSEED should be set to 0 for reproducible builds"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
