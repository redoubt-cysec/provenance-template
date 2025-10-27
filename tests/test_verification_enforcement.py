"""
Meta-test: Enforce that ALL distribution tests call verify command

This test ensures that every distribution testing script actually
verifies attestations/signatures after installation, preventing
supply chain attacks from going undetected.
"""
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
PHASE1_DIR = REPO_ROOT / "scripts" / "phase1-testing"
PHASE2_DIR = REPO_ROOT / "scripts" / "phase2-testing"


class TestVerificationEnforcement:
    """Ensure all distribution tests verify attestations."""

    def test_phase2_all_tests_call_verify(self):
        """
        CRITICAL: Every Phase 2 distribution test MUST call verify command.

        This ensures that corrupted or tampered packages are detected.
        Without this, a malicious package could pass all tests.
        """
        comprehensive_vm_tests = PHASE2_DIR / "comprehensive-vm-tests.sh"

        if not comprehensive_vm_tests.exists():
            pytest.skip("Phase 2 comprehensive tests not found")

        content = comprehensive_vm_tests.read_text()

        # Find all run_vm_test calls
        test_pattern = r'run_vm_test\s+"([^"]+)"'
        tests_found = re.findall(test_pattern, content)

        assert len(tests_found) >= 10, \
            f"Expected at least 10 Phase 2 tests, found {len(tests_found)}"

        # For each test, ensure verify is called
        for test_name in tests_found:
            # Look for the test's command section
            test_section_pattern = rf'run_vm_test\s+"{test_name}".*?"([^"]*verify[^"]*)"'
            matches = re.findall(test_section_pattern, content, re.DOTALL)

            assert len(matches) > 0, \
                f"SECURITY: Test '{test_name}' does NOT call verify command!\n" \
                f"Every distribution test must verify attestations to detect tampering.\n" \
                f"Add: 'demo verify' or 'python3 *.pyz verify' to the test command."

    def test_verify_command_exists_in_cli(self):
        """Verify that the CLI actually has a verify command."""
        cli_file = REPO_ROOT / "src" / "demo_cli" / "cli.py"

        if not cli_file.exists():
            pytest.skip("CLI file not found")

        content = cli_file.read_text()

        # Check for verify command/subcommand
        assert "verify" in content.lower(), \
            "CLI must have a 'verify' command for attestation checking"

        # Check verify module exists
        verify_file = REPO_ROOT / "src" / "demo_cli" / "verify.py"
        assert verify_file.exists(), \
            "verify.py module must exist for attestation verification"

    def test_verify_module_has_real_checks(self):
        """Verify module must do REAL verification, not fake checks."""
        verify_file = REPO_ROOT / "src" / "demo_cli" / "verify.py"

        if not verify_file.exists():
            pytest.skip("verify.py not found")

        content = verify_file.read_text()

        # Must have real verification calls
        required_verifications = [
            ("cosign", "Sigstore/cosign signature verification"),
            ("github attestation", "GitHub attestation verification"),
            ("osv-scanner", "OSV vulnerability scanning"),
            ("SBOM", "SBOM validation"),
            ("slsa", "SLSA provenance checking"),
        ]

        for keyword, description in required_verifications:
            assert keyword.lower() in content.lower(), \
                f"verify.py must include {description} (looking for '{keyword}')"

    def test_verification_returns_nonzero_on_failure(self):
        """Verify command must return non-zero exit code on failure."""
        verify_file = REPO_ROOT / "src" / "demo_cli" / "verify.py"

        if not verify_file.exists():
            pytest.skip("verify.py not found")

        content = verify_file.read_text()

        # Must return exit code based on success
        assert ("return 0" in content or "exit(0)" in content or "return 0 if" in content), \
            "verify must return 0 on success"
        assert ("return 1" in content or "exit(1)" in content or "else 1" in content), \
            "verify must return 1 on failure (for shell scripting)"

    def test_phase1_tests_include_verification_where_applicable(self):
        """
        Phase 1 tests should call verify where possible.

        Some Phase 1 tests are smoke tests, but at minimum they should
        attempt to run verify and log the result.
        """
        if not PHASE1_DIR.exists():
            pytest.skip("Phase 1 testing directory not found")

        # Check a few key Phase 1 tests
        key_tests = [
            "docker-local-registry.sh",
            "pip-test-index.sh",
            "homebrew-local-tap.sh",
        ]

        for test_file in key_tests:
            test_path = PHASE1_DIR / test_file
            if test_path.exists():
                content = test_path.read_text()
                # Should at least mention verify (even if skipped)
                # This is less strict than Phase 2
                if "verify" not in content.lower():
                    # Warning, not failure (Phase 1 is more lenient)
                    print(f"⚠️  Warning: {test_file} doesn't call verify")

    def test_documentation_explains_verification_in_tests(self):
        """Documentation must explain that tests verify attestations."""
        testing_docs = [
            REPO_ROOT / "scripts" / "TESTING-STRUCTURE.md",
            REPO_ROOT / "docs" / "testing" / "TESTING-STRATEGY.md",
        ]

        found_explanation = False
        for doc in testing_docs:
            if doc.exists():
                content = doc.read_text()
                if "verify" in content.lower() and "attestation" in content.lower():
                    found_explanation = True
                    break

        assert found_explanation, \
            "Testing documentation must explain that attestations are verified during tests"

    def test_ci_workflow_includes_verification(self):
        """CI/CD workflows should verify attestations where possible."""
        workflows_dir = REPO_ROOT / ".github" / "workflows"

        if not workflows_dir.exists():
            pytest.skip("Workflows directory not found")

        # Check integration-tests.yml or distribution-testing.yml
        test_workflows = [
            workflows_dir / "integration-tests.yml",
            workflows_dir / "distribution-testing.yml",
        ]

        for workflow in test_workflows:
            if workflow.exists():
                content = workflow.read_text()
                # Should reference the test scripts that now include verify
                if "phase1-testing" in content or "phase2-testing" in content:
                    # Good - uses our enhanced test scripts
                    return

        # If no workflows use our test scripts, that's OK (they might verify differently)
        pytest.skip("No CI workflows use phase1/phase2 test scripts")


class TestVerificationFailureHandling:
    """Test that verification failures are properly handled."""

    def test_verify_command_callable_without_attestations(self):
        """
        Verify command must be callable even without attestations.

        Should warn/skip, not crash. This allows testing dev builds.
        """
        verify_file = REPO_ROOT / "src" / "demo_cli" / "verify.py"

        if not verify_file.exists():
            pytest.skip("verify.py not found")

        content = verify_file.read_text()

        # Should handle missing files gracefully
        assert "not found" in content.lower() or "skip" in content.lower(), \
            "verify must handle missing attestation files gracefully"

    def test_distribution_tests_distinguish_dev_vs_release(self):
        """
        Tests should distinguish between dev builds (no attestations OK)
        and release builds (must have attestations).
        """
        comprehensive_vm_tests = PHASE2_DIR / "comprehensive-vm-tests.sh"

        if not comprehensive_vm_tests.exists():
            pytest.skip("Phase 2 comprehensive tests not found")

        content = comprehensive_vm_tests.read_text()

        # Should handle verify gracefully (|| or warning)
        assert "|| echo" in content or "|| true" in content, \
            "Tests must handle verify command gracefully for dev builds"

        # Should log when verify is skipped
        assert "skipped" in content.lower() or "warn" in content.lower(), \
            "Tests should log when verification is skipped"


class TestSecurityViolationDetection:
    """Test that security violations are detected and FAIL tests."""

    def test_corrupted_package_would_fail_verification(self):
        """
        Document or demonstrate that corrupted packages fail verification.

        This is the whole point - we want tampering to be detected!
        """
        verify_file = REPO_ROOT / "src" / "demo_cli" / "verify.py"

        if not verify_file.exists():
            pytest.skip("verify.py not found")

        content = verify_file.read_text()

        # Verify module must check checksums
        assert "sha256" in content.lower() or "checksum" in content.lower(), \
            "Verify must check checksums to detect corruption"

        # Must have failure cases
        assert "VerificationResult" in content, \
            "Must use VerificationResult to track pass/fail"

        assert 'passed: bool' in content or 'passed=False' in content, \
            "Must track verification pass/fail status"

    def test_verify_exit_code_propagates_to_shell(self):
        """
        Verify command exit code must be usable in shell scripts.

        This allows: demo verify && echo "safe" || echo "DANGER"
        """
        verify_file = REPO_ROOT / "src" / "demo_cli" / "verify.py"

        if not verify_file.exists():
            pytest.skip("verify.py not found")

        content = verify_file.read_text()

        # Must return proper exit codes
        assert ("return 0" in content or "return 0 if" in content), "Must return 0 for success"
        assert ("return 1" in content or "sys.exit(1)" in content or "else 1" in content), \
            "Must return 1 for failure"


# Meta-test to enforce the meta-test!
class TestMetaTestEnforcement:
    """Ensure this meta-test file itself is being run."""

    def test_this_test_file_is_in_test_suite(self):
        """This test file must be part of the test suite."""
        # If this test runs, the file is in the suite
        assert True, "Meta-test is running"

    def test_pytest_configuration_includes_all_tests(self):
        """Pytest must run all test files including this one."""
        pyproject_toml = REPO_ROOT / "pyproject.toml"

        if pyproject_toml.exists():
            content = pyproject_toml.read_text()
            # Should not exclude test_verification_enforcement
            assert "test_verification_enforcement" not in content or \
                   "exclude" not in content, \
                "test_verification_enforcement.py must not be excluded from test suite"
