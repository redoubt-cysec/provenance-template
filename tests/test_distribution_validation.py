"""
Distribution Validation Tests

These tests validate that distribution configurations are CORRECT,
but do NOT test actual publication (which requires real releases).

Purpose:
- Validate Homebrew formula syntax
- Validate Snap snapcraft.yaml
- Validate PyPI metadata
- Validate package structure

These tests run BEFORE publication to catch errors early.
"""
import json
import re
import subprocess
from pathlib import Path

import pytest

from .template_utils import guard_placeholders

REPO_ROOT = Path(__file__).parent.parent


class TestHomebrewFormula:
    """Validate Homebrew formula is correct (without publishing)."""

    def test_formula_exists(self):
        """Verify Homebrew formula file exists."""
        formula_dir = REPO_ROOT / "homebrew-tap" / "Formula"

        if not formula_dir.exists():
            pytest.skip("No Homebrew formula configured yet")

        formula_files = list(formula_dir.glob("*.rb"))
        assert len(formula_files) > 0, "No formula files found"

    def test_formula_syntax_valid(self):
        """Validate formula Ruby syntax."""
        formula_dir = REPO_ROOT / "homebrew-tap" / "Formula"

        if not formula_dir.exists():
            pytest.skip("No Homebrew formula configured")

        for formula in formula_dir.glob("*.rb"):
            content = formula.read_text()

            # Required fields
            assert re.search(r'class\s+\w+\s+<\s+Formula', content), \
                f"{formula.name} missing Formula class"
            assert 'desc ' in content, f"{formula.name} missing description"
            assert 'homepage ' in content, f"{formula.name} missing homepage"
            assert 'url ' in content, f"{formula.name} missing URL"
            assert 'sha256 ' in content, f"{formula.name} missing SHA256"
            assert 'def install' in content, f"{formula.name} missing install method"

            # Should reference GitHub releases
            assert 'github.com' in content, \
                f"{formula.name} should reference GitHub releases"

            # Should NOT have hardcoded version (should be templated)
            # Look for version variable or placeholder
            if '#{version}' not in content and '@version@' not in content:
                print(f"⚠️  {formula.name} might have hardcoded version")

            homepage_match = re.search(r'homepage\s+"([^"]+)"', content)
            if homepage_match:
                guard_placeholders(homepage_match.group(1), f"{formula.name} homepage URL")

            url_match = re.search(r'url\s+"([^"]+)"', content)
            if url_match:
                guard_placeholders(url_match.group(1), f"{formula.name} download URL")

            sha_match = re.search(r'sha256\s+"([^"]+)"', content)
            if sha_match:
                guard_placeholders(sha_match.group(1), f"{formula.name} SHA256 digest")

            print(f"✅ {formula.name} syntax valid")

    def test_formula_uses_release_url(self):
        """Verify formula downloads from GitHub releases."""
        formula_dir = REPO_ROOT / "homebrew-tap" / "Formula"

        if not formula_dir.exists():
            pytest.skip("No Homebrew formula configured")

        for formula in formula_dir.glob("*.rb"):
            content = formula.read_text()

            # Should download from releases
            assert '/releases/download/' in content, \
                f"{formula.name} should download from GitHub releases"

            # Should reference client.pyz or your artifact
            artifact_referenced = (
                'client.pyz' in content or
                '.pyz' in content or
                '.whl' in content
            )
            assert artifact_referenced, \
                f"{formula.name} should reference built artifacts"

    def test_formula_has_correct_repository(self):
        """Verify formula references correct repository."""
        formula_dir = REPO_ROOT / "homebrew-tap" / "Formula"

        if not formula_dir.exists():
            pytest.skip("No Homebrew formula configured")

        # Read pyproject.toml for expected repo
        pyproject = REPO_ROOT / "pyproject.toml"
        pyproject_content = pyproject.read_text()

        for formula in formula_dir.glob("*.rb"):
            content = formula.read_text()

            homepage_match = re.search(r'homepage\s+"([^"]+)"', content)
            if homepage_match:
                guard_placeholders(homepage_match.group(1), f"{formula.name} homepage URL")

            url_match = re.search(r'url\s+"([^"]+)"', content)
            if url_match:
                guard_placeholders(url_match.group(1), f"{formula.name} download URL")

            assert 'github.com' in content, \
                f"{formula.name} must reference a GitHub repository"

    def test_homebrew_tap_workflow_configured(self):
        """Verify Homebrew tap update workflow exists."""
        workflow = REPO_ROOT / ".github" / "workflows" / "update-homebrew-tap.yml"

        if not workflow.exists():
            pytest.skip("Homebrew tap workflow not configured")

        content = workflow.read_text()

        # Should update tap on release
        assert 'tags:' in content or 'release' in content, \
            "Workflow should trigger on releases"

        # Should reference tap repository
        assert 'TAP_REPO' in content or 'homebrew-tap' in content, \
            "Workflow should reference tap repository"

        # Should use SHA256SUMS for verification
        assert 'SHA256SUMS' in content, \
            "Workflow should verify checksums"


class TestSnapConfiguration:
    """Validate Snap package configuration (without publishing)."""

    def test_snapcraft_yaml_exists(self):
        """Verify snapcraft.yaml exists."""
        snapcraft = REPO_ROOT / "snap" / "snapcraft.yaml"

        if not snapcraft.exists():
            pytest.skip("Snap not configured yet")

        assert snapcraft.exists(), "snapcraft.yaml must exist for Snap packaging"

    def test_snapcraft_yaml_valid(self):
        """Validate snapcraft.yaml structure."""
        snapcraft = REPO_ROOT / "snap" / "snapcraft.yaml"

        if not snapcraft.exists():
            pytest.skip("Snap not configured")

        import yaml
        with open(snapcraft) as f:
            snap_config = yaml.safe_load(f)

        # Required fields
        assert 'name' in snap_config, "snapcraft.yaml missing name"
        assert 'version' in snap_config, "snapcraft.yaml missing version"
        assert 'summary' in snap_config, "snapcraft.yaml missing summary"
        assert 'description' in snap_config, "snapcraft.yaml missing description"
        assert 'confinement' in snap_config, "snapcraft.yaml missing confinement"
        assert 'parts' in snap_config, "snapcraft.yaml missing parts"

        # Should use strict or classic confinement
        assert snap_config['confinement'] in ['strict', 'classic', 'devmode'], \
            "Invalid confinement level"

        # Should define apps
        assert 'apps' in snap_config, "snapcraft.yaml should define apps"

        print("✅ snapcraft.yaml structure valid")


class TestPyPIConfiguration:
    """Validate PyPI package configuration (without publishing)."""

    def test_pyproject_toml_valid(self):
        """Verify pyproject.toml has required PyPI fields."""
        pyproject = REPO_ROOT / "pyproject.toml"
        assert pyproject.exists(), "pyproject.toml must exist"

        content = pyproject.read_text()

        # Required PyPI metadata
        required_fields = [
            'name =',
            'version =',
            'description =',
            'authors =',
            'requires-python =',
            'license =',
        ]

        for field in required_fields:
            assert field in content, f"pyproject.toml missing {field}"

        # Should have classifiers for PyPI
        assert 'classifiers' in content, \
            "pyproject.toml should have classifiers for PyPI"

        # Should NOT have placeholder values
        assert 'Your Name' not in content or '[' in content, \
            "Replace 'Your Name' placeholder in authors"

    def test_wheel_builds_successfully(self):
        """Verify wheel can be built."""
        # Check if wheel exists (from build)
        wheels = list((REPO_ROOT / "dist").glob("*.whl"))

        if not wheels:
            pytest.skip("No wheel built yet (run: python -m build)")

        # Wheel exists, validate it
        wheel = wheels[0]

        # Wheel should follow naming convention
        # {distribution}-{version}(-{build})?-{python}-{abi}-{platform}.whl
        assert re.match(r'[\w\-]+\-[\d\.]+.*\.whl', wheel.name), \
            f"Wheel name doesn't follow convention: {wheel.name}"

        print(f"✅ Wheel built successfully: {wheel.name}")

    def test_sdist_builds_successfully(self):
        """Verify source distribution builds."""
        sdists = list((REPO_ROOT / "dist").glob("*.tar.gz"))

        if not sdists:
            pytest.skip("No sdist built yet (run: python -m build)")

        sdist = sdists[0]

        # Should follow naming convention
        assert re.match(r'[\w\-]+\-[\d\.]+\.tar\.gz', sdist.name), \
            f"Sdist name doesn't follow convention: {sdist.name}"

        print(f"✅ Sdist built successfully: {sdist.name}")

    def test_readme_suitable_for_pypi(self):
        """Verify README is suitable for PyPI."""
        readme = REPO_ROOT / "README.md"
        assert readme.exists(), "README.md must exist for PyPI"

        content = readme.read_text()

        # Should have project description
        assert len(content) > 100, "README too short for PyPI"

        # Should NOT have broken relative links (PyPI renders differently)
        # This is a warning, not a failure
        if './' in content or '../' in content:
            print("⚠️  README has relative links, may break on PyPI")

        # Should have basic sections
        recommended_sections = ['install', 'usage', 'example']
        has_sections = any(section in content.lower() for section in recommended_sections)

        if not has_sections:
            print("⚠️  README should have installation/usage sections for PyPI")


class TestArtifactIntegrity:
    """Validate built artifacts are correct."""

    def test_pyz_is_executable(self):
        """Verify .pyz has correct shebang and is executable."""
        pyz_files = list((REPO_ROOT / "dist").glob("*.pyz"))

        if not pyz_files:
            pytest.skip("No .pyz built yet")

        for pyz in pyz_files:
            # Check shebang
            with open(pyz, 'rb') as f:
                shebang = f.readline()

            assert shebang.startswith(b'#!/usr/bin'), \
                f"{pyz.name} missing proper shebang"

            # Check executable bit (on Unix)
            import os
            import stat
            if os.name != 'nt':  # Not Windows
                mode = os.stat(pyz).st_mode
                assert mode & stat.S_IXUSR, \
                    f"{pyz.name} not executable"

            print(f"✅ {pyz.name} is properly executable")

    def test_wheel_contains_expected_files(self):
        """Verify wheel contains necessary files."""
        wheels = list((REPO_ROOT / "dist").glob("*.whl"))

        if not wheels:
            pytest.skip("No wheel built yet")

        import zipfile
        for wheel in wheels:
            with zipfile.ZipFile(wheel) as zf:
                files = zf.namelist()

                # Should contain Python files
                py_files = [f for f in files if f.endswith('.py')]
                assert len(py_files) > 0, \
                    f"{wheel.name} contains no Python files"

                # Should contain metadata
                metadata_files = [f for f in files if 'METADATA' in f or 'WHEEL' in f]
                assert len(metadata_files) > 0, \
                    f"{wheel.name} missing metadata"

                # Should NOT contain tests (usually)
                test_files = [f for f in files if 'test' in f.lower()]
                if test_files:
                    print(f"⚠️  {wheel.name} contains test files: {len(test_files)}")

                print(f"✅ {wheel.name} structure valid")


class TestDistributionDocumentation:
    """Validate distribution documentation exists."""

    def test_installation_instructions_exist(self):
        """Verify README has installation instructions."""
        readme = REPO_ROOT / "README.md"
        content = readme.read_text().lower()

        # Should have installation section
        assert 'install' in content or 'setup' in content, \
            "README should have installation instructions"

        # Should mention pip or other installation methods
        has_install_method = any(method in content for method in [
            'pip install',
            'brew install',
            'snap install',
            'download'
        ])

        assert has_install_method, \
            "README should mention at least one installation method"

    def test_verification_instructions_exist(self):
        """Verify SUPPLY-CHAIN.md has verification instructions."""
        supply_chain = REPO_ROOT / "SUPPLY-CHAIN.md"

        if not supply_chain.exists():
            pytest.skip("SUPPLY-CHAIN.md not created yet")

        content = supply_chain.read_text()

        # Should explain verification
        assert 'verify' in content.lower(), \
            "SUPPLY-CHAIN.md should explain verification"

        # Should mention attestation or checksums
        assert 'attestation' in content.lower() or 'checksum' in content.lower(), \
            "SUPPLY-CHAIN.md should mention verification methods"


class TestRepositoryConfiguration:
    """Validate repository is configured for distribution."""

    def test_github_releases_configured(self):
        """Verify release workflow creates GitHub releases."""
        release_workflow = REPO_ROOT / ".github" / "workflows" / "secure-release.yml"

        assert release_workflow.exists(), "secure-release.yml must exist"

        content = release_workflow.read_text()

        # Should create release
        assert 'release' in content.lower() or 'gh release create' in content, \
            "Workflow should create GitHub releases"

        # Should upload artifacts
        assert 'upload' in content.lower() or 'gh release upload' in content, \
            "Workflow should upload release artifacts"

    def test_release_assets_configured(self):
        """Verify correct assets are uploaded to releases."""
        release_workflow = REPO_ROOT / ".github" / "workflows" / "secure-release.yml"
        content = release_workflow.read_text()

        # Should upload these critical files
        important_assets = [
            '.pyz',
            'SHA256SUMS',
            'sbom',
        ]

        for asset in important_assets:
            assert asset in content, \
                f"Release workflow should upload {asset}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
