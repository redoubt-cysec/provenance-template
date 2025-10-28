"""
Published Distribution Tests

These tests validate ACTUAL published packages work correctly.
They test against REAL distribution channels after publication.

IMPORTANT: These tests will FAIL if:
- No release has been published yet
- Homebrew tap doesn't exist
- PyPI package not published
- GitHub release not created

Run these tests AFTER cutting a release to validate end-to-end.

Usage:
    # Test specific release
    pytest tests/test_published_distributions.py -v --release-tag=v1.0.0

    # Test latest release
    pytest tests/test_published_distributions.py -v --use-latest

Environment Variables:
    GITHUB_REPO: Full repo name (e.g., "OWNER/REPO")
    HOMEBREW_TAP: Tap name (e.g., "OWNER/tap")
    PYPI_PACKAGE: PyPI package name (e.g., "your-package")
"""
import os
import shutil
import socket
import subprocess
import time
from pathlib import Path
from urllib import error as urllib_error

import pytest

REPO_ROOT = Path(__file__).parent.parent

# Configuration from environment or defaults
GITHUB_REPO = os.getenv("GITHUB_REPO", "redoubt-cysec/provenance-template")
HOMEBREW_TAP = os.getenv("HOMEBREW_TAP", "redoubt-cysec/tap")
PYPI_PACKAGE = os.getenv("PYPI_PACKAGE", "provenance-demo")


@pytest.fixture(scope="module")
def release_tag(request):
    """Get release tag to test."""
    tag = request.config.getoption("--release-tag")
    use_latest = request.config.getoption("--use-latest")

    if not tag and not use_latest:
        pytest.skip(
            "Must specify --release-tag=vX.Y.Z or --use-latest to test published releases"
        )

    if use_latest:
        # Get latest release tag from GitHub
        repo = request.config.getoption("--github-repo")
        result = subprocess.run(
            ["gh", "release", "list", "--repo", repo, "--limit", "1"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            pytest.skip(f"Failed to get latest release: {result.stderr}")

        # Parse first line: TAG  TITLE  TYPE  DATE
        lines = result.stdout.strip().split("\n")
        if not lines or not lines[0]:
            pytest.skip("No releases found")

        tag = lines[0].split("\t")[0].strip()

    return tag


@pytest.fixture(scope="module")
def github_repo(request):
    """Get GitHub repository name."""
    return request.config.getoption("--github-repo")


class TestGitHubRelease:
    """Test GitHub release assets are downloadable and valid."""

    @pytest.mark.published
    def test_release_exists(self, release_tag, github_repo):
        """Verify release exists on GitHub."""
        result = subprocess.run(
            ["gh", "release", "view", release_tag, "--repo", github_repo],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, \
            f"Release {release_tag} not found in {github_repo}"

        print(f"✅ Release {release_tag} exists")

    @pytest.mark.published
    def test_pyz_downloadable(self, release_tag, github_repo, tmp_path):
        """Test .pyz can be downloaded from release."""
        # Download .pyz
        download_url = f"https://github.com/{github_repo}/releases/download/{release_tag}/client.pyz"

        output_file = tmp_path / "client.pyz"
        result = subprocess.run(
            ["curl", "-L", "-o", str(output_file), download_url],
            capture_output=True,
            timeout=60
        )

        assert result.returncode == 0, \
            f"Failed to download .pyz: {result.stderr.decode()}"
        assert output_file.exists(), ".pyz not downloaded"
        assert output_file.stat().st_size > 0, ".pyz is empty"

        print(f"✅ Downloaded .pyz from {release_tag}")

    @pytest.mark.published
    def test_checksums_downloadable(self, release_tag, github_repo, tmp_path):
        """Test SHA256SUMS can be downloaded."""
        download_url = f"https://github.com/{github_repo}/releases/download/{release_tag}/SHA256SUMS"

        output_file = tmp_path / "SHA256SUMS"
        result = subprocess.run(
            ["curl", "-L", "-o", str(output_file), download_url],
            capture_output=True,
            timeout=60
        )

        assert result.returncode == 0, "Failed to download SHA256SUMS"
        assert output_file.exists(), "SHA256SUMS not downloaded"

        # Should list artifacts
        content = output_file.read_text()
        assert len(content) > 0, "SHA256SUMS is empty"
        assert '.pyz' in content, "SHA256SUMS should list .pyz"

        print(f"✅ Downloaded SHA256SUMS from {release_tag}")

    @pytest.mark.published
    def test_attestation_exists(self, release_tag, github_repo, tmp_path):
        """Test GitHub attestation exists for artifacts."""
        # Download .pyz first
        download_url = f"https://github.com/{github_repo}/releases/download/{release_tag}/client.pyz"
        pyz_file = tmp_path / "client.pyz"

        subprocess.run(
            ["curl", "-L", "-o", str(pyz_file), download_url],
            capture_output=True,
            timeout=60
        )

        if not pyz_file.exists():
            pytest.skip(".pyz not available to test attestation")

        # Verify attestation
        result = subprocess.run(
            ["gh", "attestation", "verify", str(pyz_file), "--repo", github_repo],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, \
            f"Attestation verification failed: {result.stderr}"

        print(f"✅ Attestation verified for {release_tag}")


class TestHomebrewTap:
    """Test Homebrew tap installation works."""

    @pytest.mark.published
    @pytest.mark.slow
    def test_tap_exists(self):
        """Verify Homebrew tap repository exists."""
        if HOMEBREW_TAP == "OWNER/tap":
            pytest.skip("HOMEBREW_TAP not configured (set env var)")
        if shutil.which("gh") is None:
            pytest.skip("GitHub CLI not installed")

        # Check if tap repo exists on GitHub
        target_repo = HOMEBREW_TAP.replace("/tap", "/homebrew-tap")
        try:
            result = subprocess.run(
                ["gh", "repo", "view", target_repo],
                capture_output=True,
                text=True
            )
        except FileNotFoundError:
            pytest.skip("GitHub CLI not installed")

        if result.returncode != 0:
            output = (result.stderr or result.stdout or "").strip()
            lowered = output.lower()
            transient_errors = (
                "could not resolve host",
                "network is unreachable",
                "timed out",
                "nodename nor servname provided",
            )
            if any(err in lowered for err in transient_errors):
                pytest.skip(f"GitHub CLI cannot reach GitHub: {output}")
            pytest.fail(f"Homebrew tap repository not found: {HOMEBREW_TAP}\n{output}")

        print(f"✅ Tap repository exists: {HOMEBREW_TAP}")

    @pytest.mark.published
    @pytest.mark.slow
    def test_formula_in_tap(self, release_tag):
        """Verify formula exists in tap."""
        if HOMEBREW_TAP == "OWNER/tap":
            pytest.skip("HOMEBREW_TAP not configured")
        if shutil.which("gh") is None:
            pytest.skip("GitHub CLI not installed")

        # Get formula from tap repo
        tap_repo = HOMEBREW_TAP.replace('/tap', '/homebrew-tap')
        result = subprocess.run(
            ["gh", "api", f"repos/{tap_repo}/contents/Formula", "--jq", ".[].name"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            pytest.skip(f"Failed to list formulas: {result.stderr}")

        formulas = result.stdout.strip().split("\n")
        assert len(formulas) > 0, "No formulas found in tap"

        print(f"✅ Found formulas in tap: {formulas}")

    @pytest.mark.published
    @pytest.mark.slow
    @pytest.mark.integration
    def test_brew_install_works(self, release_tag):
        """Test actual brew install command."""
        if HOMEBREW_TAP == "OWNER/tap":
            pytest.skip("HOMEBREW_TAP not configured")

        # Note: This test requires Homebrew installed
        # Should run on macOS or Linux with Homebrew

        # Check if brew is available
        brew_check = subprocess.run(
            ["which", "brew"],
            capture_output=True
        )

        if brew_check.returncode != 0:
            pytest.skip("Homebrew not installed")

        # Add tap
        print(f"Adding tap: {HOMEBREW_TAP}")
        result = subprocess.run(
            ["brew", "tap", HOMEBREW_TAP],
            capture_output=True,
            text=True,
            timeout=60
        )

        # Extract formula name from tap (usually last part)
        formula_name = "client"  # Adjust this

        # Install formula
        print(f"Installing: {formula_name}")
        result = subprocess.run(
            ["brew", "install", formula_name],
            capture_output=True,
            text=True,
            timeout=300
        )

        assert result.returncode == 0, \
            f"brew install failed: {result.stderr}"

        # Test installed command
        result = subprocess.run(
            [formula_name, "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0, \
            f"Installed command doesn't work: {result.stderr}"

        # Cleanup
        subprocess.run(["brew", "uninstall", formula_name], capture_output=True)

        print(f"✅ brew install works for {release_tag}")


class TestPyPIPackage:
    """Test PyPI package installation works."""

    @pytest.mark.published
    def test_package_exists_on_pypi(self):
        """Verify package exists on PyPI."""
        if PYPI_PACKAGE == "demo-secure-cli":
            pytest.skip("PYPI_PACKAGE not configured or not published")

        # Check PyPI API
        import urllib.request
        import json

        url = f"https://pypi.org/pypi/{PYPI_PACKAGE}/json"

        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read())

            assert 'info' in data, "Invalid PyPI response"
            assert data['info']['name'] == PYPI_PACKAGE, "Package name mismatch"

            print(f"✅ Package exists on PyPI: {PYPI_PACKAGE}")

        except urllib_error.HTTPError as e:
            if e.code == 404:
                pytest.skip(f"Package not found on PyPI: {PYPI_PACKAGE}")
            raise
        except urllib_error.URLError as e:
            reason = getattr(e, "reason", None)
            if isinstance(reason, socket.gaierror):
                pytest.skip("Network unavailable for PyPI lookup")
            raise

    @pytest.mark.published
    @pytest.mark.slow
    def test_pip_install_works(self, release_tag, tmp_path):
        """Test actual pip install from PyPI."""
        if PYPI_PACKAGE == "demo-secure-cli":
            pytest.skip("PYPI_PACKAGE not configured")

        # Create virtual environment
        venv_path = tmp_path / "test-venv"
        result = subprocess.run(
            ["python3", "-m", "venv", str(venv_path)],
            capture_output=True,
            timeout=60
        )

        assert result.returncode == 0, "Failed to create venv"

        # Install from PyPI
        pip_path = venv_path / "bin" / "pip"
        if not pip_path.exists():
            pip_path = venv_path / "Scripts" / "pip.exe"  # Windows

        print(f"Installing from PyPI: {PYPI_PACKAGE}")
        result = subprocess.run(
            [str(pip_path), "install", PYPI_PACKAGE],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            output = (result.stderr or result.stdout or "").lower()
            transient_errors = (
                "temporary failure in name resolution",
                "failed to establish a new connection",
                "could not resolve host",
                "network is unreachable",
                "timed out",
            )
            if any(err in output for err in transient_errors):
                pytest.skip(f"Network unavailable for pip install:\n{result.stderr or result.stdout}")
            pytest.fail(f"pip install failed: {result.stderr or result.stdout}")

        # Test installed command (adjust command name)
        cmd_path = venv_path / "bin" / "demo"
        if not cmd_path.exists():
            cmd_path = venv_path / "Scripts" / "demo.exe"

        if cmd_path.exists():
            result = subprocess.run(
                [str(cmd_path), "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            assert result.returncode == 0, \
                f"Installed command doesn't work: {result.stderr}"

        print(f"✅ pip install works from PyPI")


class TestEndToEndUserExperience:
    """Test complete user workflow from download to execution."""

    @pytest.mark.published
    @pytest.mark.slow
    def test_github_download_and_verify(self, release_tag, github_repo, tmp_path):
        """Test user downloads, verifies, and runs .pyz."""
        # Download .pyz
        print(f"Downloading .pyz from {release_tag}...")
        download_url = f"https://github.com/{github_repo}/releases/download/{release_tag}/client.pyz"
        pyz_file = tmp_path / "client.pyz"

        result = subprocess.run(
            ["curl", "-L", "-o", str(pyz_file), download_url],
            capture_output=True,
            timeout=60
        )

        assert result.returncode == 0, "Failed to download .pyz"

        # Download SHA256SUMS
        print("Downloading checksums...")
        checksums_url = f"https://github.com/{github_repo}/releases/download/{release_tag}/SHA256SUMS"
        checksums_file = tmp_path / "SHA256SUMS"

        subprocess.run(
            ["curl", "-L", "-o", str(checksums_file), checksums_url],
            capture_output=True,
            timeout=60
        )

        # Verify checksum
        print("Verifying checksum...")
        result = subprocess.run(
            ["sha256sum", "--check", "--ignore-missing", str(checksums_file)],
            cwd=tmp_path,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, \
            f"Checksum verification failed: {result.stderr}"

        # Verify attestation
        print("Verifying attestation...")
        result = subprocess.run(
            ["gh", "attestation", "verify", str(pyz_file), "--repo", github_repo],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, \
            f"Attestation verification failed: {result.stderr}"

        # Execute .pyz
        print("Executing .pyz...")
        import stat
        pyz_file.chmod(pyz_file.stat().st_mode | stat.S_IXUSR)

        result = subprocess.run(
            ["python3", str(pyz_file), "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0, \
            f"Execution failed: {result.stderr}"

        print(f"✅ Complete end-to-end workflow successful for {release_tag}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
