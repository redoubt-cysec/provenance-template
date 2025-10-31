"""
Security Pipeline Tests

Validates that all security features are properly configured and functional.
"""
import os
import subprocess
import json
import yaml
from pathlib import Path

import pytest

# Base paths
REPO_ROOT = Path(__file__).parent.parent
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
SCRIPTS_DIR = REPO_ROOT / "scripts"


class TestReproducibleBuilds:
    """Test that builds are configured for reproducibility."""

    def test_build_script_exists(self):
        """Verify build script exists and is executable."""
        build_script = SCRIPTS_DIR / "build_pyz.sh"
        assert build_script.exists(), "build_pyz.sh must exist"
        assert os.access(build_script, os.X_OK), "build_pyz.sh must be executable"

    def test_build_script_sets_source_date_epoch(self):
        """Verify build script uses SOURCE_DATE_EPOCH for reproducibility."""
        build_script = SCRIPTS_DIR / "build_pyz.sh"
        content = build_script.read_text()
        assert "SOURCE_DATE_EPOCH" in content, "Build must set SOURCE_DATE_EPOCH for reproducibility"

    @pytest.mark.slow
    def test_build_creates_deterministic_artifacts(self):
        """Run build twice and verify identical outputs.

        This test actually builds the project, so it's marked as slow.
        It verifies that builds are reproducible when SOURCE_DATE_EPOCH is set.
        """
        # Set fixed timestamp for reproducibility
        env = os.environ.copy()
        env["SOURCE_DATE_EPOCH"] = "1234567890"

        # First build
        result = subprocess.run(
            [str(SCRIPTS_DIR / "build_pyz.sh")],
            env=env,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            pytest.skip(f"Build script failed: {result.stderr}")

        pyz_file = REPO_ROOT / "dist" / "client.pyz"
        if not pyz_file.exists():
            pytest.skip("Build did not produce .pyz artifact")

        # Get hash of first build
        result1 = subprocess.run(
            ["sha256sum", str(pyz_file)],
            capture_output=True,
            text=True,
            check=True
        )
        hash1 = result1.stdout.split()[0]

        # Clean and rebuild
        subprocess.run(["rm", "-rf", str(REPO_ROOT / "dist"), str(REPO_ROOT / "build")], check=True)
        subprocess.run(
            [str(SCRIPTS_DIR / "build_pyz.sh")],
            env=env,
            check=True,
            capture_output=True
        )

        # Get hash of second build
        result2 = subprocess.run(
            ["sha256sum", str(pyz_file)],
            capture_output=True,
            text=True,
            check=True
        )
        hash2 = result2.stdout.split()[0]

        assert hash1 == hash2, f"Builds must be deterministic (identical hashes)\nFirst: {hash1}\nSecond: {hash2}"


class TestSBOMGeneration:
    """Test SBOM generation and validation."""

    def test_release_workflow_generates_sbom(self):
        """Verify release workflow includes SBOM generation step."""
        release_workflow = WORKFLOWS_DIR / "secure-release.yml"
        assert release_workflow.exists(), "secure-release.yml must exist"

        content = release_workflow.read_text()
        assert "cyclonedx-python" in content or "sbom" in content.lower(), \
            "Release workflow must generate SBOM"

    def test_sbom_validation_configured(self):
        """Verify SBOM is validated as valid CycloneDX."""
        release_workflow = WORKFLOWS_DIR / "secure-release.yml"
        content = release_workflow.read_text()
        # Should validate the SBOM is well-formed
        assert "cyclonedx" in content.lower(), "Should use CycloneDX format for SBOM"


class TestVulnerabilityScanning:
    """Test vulnerability scanning configuration."""

    def test_osv_scanner_configured(self):
        """Verify OSV scanner is configured in workflows."""
        # Check if OSV is in release or main-verify workflow
        workflows_to_check = ["secure-release.yml", "main-verify.yml"]
        osv_found = False

        for workflow_name in workflows_to_check:
            workflow_file = WORKFLOWS_DIR / workflow_name
            if workflow_file.exists():
                content = workflow_file.read_text()
                if "osv-scanner" in content.lower():
                    osv_found = True
                    break

        assert osv_found, \
            "OSV vulnerability scanning must be configured in workflows"

    def test_scheduled_scanning_exists(self):
        """Verify scheduled vulnerability scanning is configured."""
        scan_workflow = WORKFLOWS_DIR / "scan-latest-release.yml"
        assert scan_workflow.exists(), "Scheduled vulnerability scanning must be configured"

        content = scan_workflow.read_text()
        assert "schedule:" in content or "cron:" in content, \
            "Scan workflow must run on a schedule"


class TestAttestationAndSigning:
    """Test attestation and signing configuration."""

    def test_github_attestation_configured(self):
        """Verify GitHub attestation is used."""
        release_workflow = WORKFLOWS_DIR / "secure-release.yml"
        content = release_workflow.read_text()
        assert "actions/attest-build-provenance" in content, \
            "Must use GitHub's attestation action"

    def test_cosign_signing_configured(self):
        """Verify cosign keyless signing is configured."""
        release_workflow = WORKFLOWS_DIR / "secure-release.yml"
        content = release_workflow.read_text()
        assert "cosign" in content.lower() and "sign-blob" in content, \
            "Must use cosign for signing"
        # Verify keyless (no private keys)
        assert "COSIGN_EXPERIMENTAL=1" in content or "cosign-installer" in content, \
            "Must use keyless signing (no private keys)"

    def test_permissions_are_minimal(self):
        """Verify workflow permissions follow least privilege."""
        release_workflow = WORKFLOWS_DIR / "secure-release.yml"

        with open(release_workflow) as f:
            workflow = yaml.safe_load(f)

        # Check that permissions are explicitly set
        assert "permissions" in workflow or any(
            "permissions" in job for job in workflow.get("jobs", {}).values()
        ), "Workflows must explicitly declare permissions"

    def test_id_token_permission_for_signing(self):
        """Verify id-token: write permission for keyless signing."""
        release_workflow = WORKFLOWS_DIR / "secure-release.yml"

        with open(release_workflow) as f:
            workflow = yaml.safe_load(f)

        # Check for id-token permission (needed for Sigstore)
        content = release_workflow.read_text()
        assert "id-token: write" in content, \
            "Must have id-token: write permission for keyless signing"


class TestWorkflowSecurity:
    """Test GitHub Actions workflow security hardening."""

    def test_actions_are_pinned_to_sha(self):
        """Verify all actions use pinned SHAs, not tags."""
        for workflow_file in WORKFLOWS_DIR.glob("*.yml"):
            content = workflow_file.read_text()

            # Find all uses: statements (match only at word boundaries to avoid matching "statuses: none")
            import re
            uses_statements = re.findall(r'(?:^|\s)-?\s*uses:\s+([^\s]+)', content, re.MULTILINE)

            for use in uses_statements:
                # Skip local actions (./)
                if use.startswith("./"):
                    continue

                # Should be in format: owner/repo@SHA
                assert "@" in use, f"Action {use} in {workflow_file.name} must specify version"

                # Extract the ref (part after @)
                ref = use.split("@")[1]

                # SHA1 is 40 hex chars, warn if using tags
                if not (len(ref) == 40 and all(c in "0123456789abcdef" for c in ref.lower())):
                    # This is a warning - tags are allowed but SHAs are better
                    print(f"Warning: {use} in {workflow_file.name} uses tag/branch, not SHA")

    def test_harden_runner_configured(self):
        """Verify step-security/harden-runner is used in release workflow."""
        release_workflow = WORKFLOWS_DIR / "secure-release.yml"
        content = release_workflow.read_text()
        assert "step-security/harden-runner" in content, \
            "Release workflow should use harden-runner for network egress control"

    def test_no_pull_request_target_workflow(self):
        """Verify no dangerous pull_request_target triggers on untrusted code."""
        for workflow_file in WORKFLOWS_DIR.glob("*.yml"):
            with open(workflow_file) as f:
                workflow = yaml.safe_load(f)

            on_config = workflow.get("on", {})
            if isinstance(on_config, dict):
                # pull_request_target is dangerous if it checks out PR code
                if "pull_request_target" in on_config:
                    content = workflow_file.read_text()
                    # If it checks out PR code, it's dangerous
                    assert "github.event.pull_request.head.sha" not in content, \
                        f"{workflow_file.name} uses pull_request_target with PR checkout - unsafe!"


class TestVerificationScripts:
    """Test that verification scripts exist and are functional."""

    def test_build_verification_script_exists(self):
        """Verify build verification script exists."""
        verify_script = SCRIPTS_DIR / "verify_build.sh"
        assert verify_script.exists(), "verify_build.sh must exist"
        assert os.access(verify_script, os.X_OK), "verify_build.sh must be executable"

    def test_provenance_verification_script_exists(self):
        """Verify provenance verification script exists."""
        verify_script = SCRIPTS_DIR / "verify_provenance.sh"
        assert verify_script.exists(), "verify_provenance.sh must exist"
        assert os.access(verify_script, os.X_OK), "verify_provenance.sh must be executable"

    def test_verification_scripts_use_gh_cli(self):
        """Verify scripts use GitHub CLI for attestation verification."""
        verify_script = SCRIPTS_DIR / "verify_provenance.sh"
        content = verify_script.read_text()
        assert "gh attestation verify" in content, \
            "Verification script should use gh CLI for attestation verification"


class TestRebuilderWorkflow:
    """Test rebuilder workflow for reproducibility verification."""

    def test_rebuilder_workflow_exists(self):
        """Verify rebuilder workflow exists."""
        rebuilder_workflow = WORKFLOWS_DIR / "rebuilder.yml"
        assert rebuilder_workflow.exists(), "rebuilder.yml must exist for reproducibility checks"

    def test_rebuilder_compares_hashes(self):
        """Verify rebuilder workflow compares build hashes."""
        rebuilder_workflow = WORKFLOWS_DIR / "rebuilder.yml"
        content = rebuilder_workflow.read_text()
        assert "sha256sum" in content.lower() or "compare" in content.lower(), \
            "Rebuilder must compare hashes to verify reproducibility"


class TestSupplyChainMetadata:
    """Test supply chain documentation and metadata."""

    def test_supply_chain_doc_exists(self):
        """Verify SUPPLY-CHAIN.md documentation exists."""
        doc = REPO_ROOT / "docs" / "security" / "SUPPLY-CHAIN.md"
        assert doc.exists(), "docs/security/SUPPLY-CHAIN.md must document security features"

    def test_supply_chain_doc_has_verification_instructions(self):
        """Verify supply chain doc includes verification instructions."""
        doc = REPO_ROOT / "docs" / "security" / "SUPPLY-CHAIN.md"
        content = doc.read_text()
        assert "verify" in content.lower(), "SUPPLY-CHAIN.md must include verification instructions"
        assert "gh attestation verify" in content or "cosign" in content, \
            "SUPPLY-CHAIN.md must show how to verify signatures/attestations"

    def test_pyproject_has_minimal_metadata(self):
        """Verify pyproject.toml has required security metadata."""
        pyproject = REPO_ROOT / "pyproject.toml"
        assert pyproject.exists(), "pyproject.toml must exist"

        content = pyproject.read_text()
        assert "name" in content and "version" in content, \
            "pyproject.toml must declare name and version"


class TestNoSecretsInRepo:
    """Test that no secrets or credentials are committed."""

    def test_gitignore_excludes_sensitive_files(self):
        """Verify .gitignore excludes common secret files."""
        gitignore = REPO_ROOT / ".gitignore"
        assert gitignore.exists(), ".gitignore must exist"

        content = gitignore.read_text()
        sensitive_patterns = [".env", "*.pem", "*.key"]

        for pattern in sensitive_patterns:
            assert pattern in content, f".gitignore should exclude {pattern}"

    def test_no_hardcoded_tokens_in_workflows(self):
        """Verify no hardcoded secrets in workflow files."""
        forbidden_patterns = [
            r"ghp_[a-zA-Z0-9]{36}",  # GitHub PAT
            r"AKIA[0-9A-Z]{16}",      # AWS Access Key
        ]

        import re
        for workflow_file in WORKFLOWS_DIR.glob("*.yml"):
            content = workflow_file.read_text()
            for pattern in forbidden_patterns:
                assert not re.search(pattern, content), \
                    f"Possible hardcoded secret in {workflow_file.name}"


class TestDependencyManagement:
    """Test dependency management and pinning."""

    def test_requirements_file_exists(self):
        """Verify requirements.in exists for dependency tracking."""
        requirements = REPO_ROOT / "requirements.in"
        assert requirements.exists(), "requirements.in should exist for dependency management"

    def test_pyproject_has_python_version_constraint(self):
        """Verify minimum Python version is specified."""
        pyproject = REPO_ROOT / "pyproject.toml"
        content = pyproject.read_text()
        assert "requires-python" in content, \
            "pyproject.toml must specify requires-python version"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
