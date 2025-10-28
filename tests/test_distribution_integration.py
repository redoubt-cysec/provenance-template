"""
Distribution Integration Tests

IMPORTANT: These tests validate LOCAL builds work correctly across platforms.
They do NOT test actual publication to Homebrew/PyPI/Snap stores.

What These Tests Do:
- ✅ Test that built .pyz works on fresh OS installations
- ✅ Test that wheels install correctly via pip
- ✅ Test cross-platform Python compatibility
- ✅ Validate distribution configurations (syntax, structure)

What These Tests DON'T Do:
- ❌ Test actual Homebrew tap installation (requires published tap)
- ❌ Test actual PyPI publication (requires PyPI credentials)
- ❌ Test actual Snap store installation (requires published snap)
- ❌ Test Winget installation (requires published package)

For actual distribution testing, see:
- test_distribution_validation.py - Validates configs are correct
- GitHub workflow integration-tests.yml - Tests on real platforms

Requirements:
- multipass installed: https://multipass.run/
- Sufficient disk space for VMs (~2GB per VM)
- Network access for package downloads
- Built artifacts in dist/ directory

Run with: pytest tests/test_distribution_integration.py -v -s
"""
import json
import os
import subprocess
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
HOMEBREW_TAP = os.getenv("HOMEBREW_TAP", "OWNER/tap")


def multipass_available():
    """Check if multipass is installed and available."""
    try:
        subprocess.run(
            ["multipass", "version"],
            capture_output=True,
            check=True,
            timeout=5
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def multipass_exec(vm_name: str, command: str, timeout: int = 120):
    """Execute command in multipass VM."""
    result = subprocess.run(
        ["multipass", "exec", vm_name, "--", "bash", "-c", command],
        capture_output=True,
        text=True,
        timeout=timeout
    )
    return result


def create_vm(name: str, image: str = "22.04", cpus: int = 2, mem: str = "2G", disk: str = "5G"):
    """Create a multipass VM."""
    result = subprocess.run(
        ["multipass", "launch", image, "--name", name, "--cpus", str(cpus), "--memory", mem, "--disk", disk],
        capture_output=True,
        text=True,
        timeout=300  # 5 minutes for VM creation
    )
    return result.returncode == 0


def delete_vm(name: str):
    """Delete a multipass VM."""
    subprocess.run(["multipass", "delete", name], capture_output=True)
    subprocess.run(["multipass", "purge"], capture_output=True)


@pytest.fixture(scope="module")
def ubuntu_vm():
    """Create Ubuntu VM for testing."""
    if not multipass_available():
        pytest.skip("Multipass not available")

    vm_name = "cli-test-ubuntu"

    # Cleanup any existing VM
    delete_vm(vm_name)

    # Create fresh VM
    if not create_vm(vm_name, image="22.04"):
        pytest.skip(f"Failed to create VM: {vm_name}")

    # Wait for VM to be ready
    time.sleep(10)

    yield vm_name

    # Cleanup
    delete_vm(vm_name)


@pytest.fixture(scope="module")
def macos_vm():
    """Create macOS VM for testing (if on macOS host)."""
    if not multipass_available():
        pytest.skip("Multipass not available")

    # Check if we're on macOS (multipass on mac can use macOS VMs)
    import platform
    if platform.system() != "Darwin":
        pytest.skip("macOS VM only available on macOS host")

    vm_name = "cli-test-macos"

    # Cleanup any existing VM
    delete_vm(vm_name)

    # On macOS, multipass uses Ubuntu by default, but we can test Homebrew
    if not create_vm(vm_name, image="22.04"):
        pytest.skip(f"Failed to create VM: {vm_name}")

    time.sleep(10)

    yield vm_name

    # Cleanup
    delete_vm(vm_name)


class TestHomebrewInstallation:
    """Test Homebrew tap installation and execution."""

    @pytest.mark.slow
    @pytest.mark.integration
    def test_homebrew_tap_install(self, macos_vm):
        """Test installation via Homebrew tap."""
        vm_name = macos_vm

        # Install Homebrew
        print(f"\n[{vm_name}] Installing Homebrew...")
        result = multipass_exec(
            vm_name,
            'NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
            timeout=600
        )

        if result.returncode != 0:
            pytest.skip(f"Failed to install Homebrew: {result.stderr}")

        # Add Homebrew to PATH
        brew_path = multipass_exec(vm_name, "test -d /home/linuxbrew/.linuxbrew && echo /home/linuxbrew/.linuxbrew/bin || echo /usr/local/bin")

        # Add tap (replace with actual tap)
        print(f"[{vm_name}] Adding tap...")
        if HOMEBREW_TAP == "OWNER/tap":
            pytest.skip("HOMEBREW_TAP not configured for integration test")
        result = multipass_exec(
            vm_name,
            f'{brew_path.stdout.strip()}/brew tap {HOMEBREW_TAP} || true',
            timeout=60
        )

        # Note: This will fail until the tap is actually published
        # For now, we test the workflow by installing a .pyz directly

        # Alternative: Download and install .pyz
        print(f"[{vm_name}] Testing .pyz installation...")

        # Copy local .pyz to VM (if it exists)
        pyz_file = REPO_ROOT / "dist" / "provenance-demo.pyz"
        if not pyz_file.exists():
            pytest.skip("No .pyz file to test (run build first)")

        # Transfer file to VM
        subprocess.run(
            ["multipass", "transfer", str(pyz_file), f"{vm_name}:/tmp/provenance-demo.pyz"],
            capture_output=True,
            timeout=30
        )

        # Make executable and run
        result = multipass_exec(
            vm_name,
            "chmod +x /tmp/provenance-demo.pyz && /tmp/provenance-demo.pyz --version",
            timeout=10
        )

        assert result.returncode == 0, f"Failed to run .pyz: {result.stderr}"
        assert "0.1.0" in result.stdout, "Version output incorrect"

        print(f"[{vm_name}] ✅ .pyz works correctly")

    @pytest.mark.slow
    @pytest.mark.integration
    def test_homebrew_formula_valid(self):
        """Test that Homebrew formula syntax is valid."""
        formula_dir = REPO_ROOT / "homebrew-tap" / "Formula"

        if not formula_dir.exists():
            pytest.skip("No Homebrew formula directory")

        # Find formula files
        formula_files = list(formula_dir.glob("*.rb"))

        if not formula_files:
            pytest.skip("No Homebrew formulas found")

        for formula in formula_files:
            # Basic syntax validation
            content = formula.read_text()

            # Must have required fields
            assert 'class ' in content, f"{formula.name} missing class definition"
            assert 'desc ' in content, f"{formula.name} missing description"
            assert 'homepage ' in content, f"{formula.name} missing homepage"
            assert 'url ' in content, f"{formula.name} missing URL"
            assert 'sha256 ' in content, f"{formula.name} missing SHA256"

            print(f"✅ {formula.name} syntax valid")


class TestSnapInstallation:
    """Test Snap package installation and execution."""

    @pytest.mark.slow
    @pytest.mark.integration
    def test_snap_install(self, ubuntu_vm):
        """Test installation via Snap."""
        vm_name = ubuntu_vm

        # Ensure snapd is installed and running
        print(f"\n[{vm_name}] Setting up snapd...")
        result = multipass_exec(
            vm_name,
            "sudo apt-get update && sudo apt-get install -y snapd && sudo systemctl start snapd",
            timeout=300
        )

        if result.returncode != 0:
            pytest.skip(f"Failed to setup snapd: {result.stderr}")

        # Wait for snapd to be ready
        time.sleep(10)

        # For now, test that snap works
        result = multipass_exec(vm_name, "snap version", timeout=10)
        assert result.returncode == 0, "snapd not working"

        print(f"[{vm_name}] ✅ snapd ready")

        # Note: Actual snap installation requires published snap
        # We can test local snap installation with --dangerous flag
        # For template purposes, we validate the snap can be built

        print(f"[{vm_name}] Snap infrastructure verified")


class TestPipInstallation:
    """Test pip/PyPI installation and execution."""

    @pytest.mark.slow
    @pytest.mark.integration
    def test_pip_install_from_wheel(self, ubuntu_vm):
        """Test installation via pip from wheel."""
        vm_name = ubuntu_vm

        # Install Python and pip
        print(f"\n[{vm_name}] Installing Python and pip...")
        result = multipass_exec(
            vm_name,
            "sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv",
            timeout=300
        )

        if result.returncode != 0:
            pytest.skip(f"Failed to install Python: {result.stderr}")

        # Check for built wheel
        wheel_files = list((REPO_ROOT / "dist").glob("*.whl"))
        if not wheel_files:
            pytest.skip("No wheel file to test (run build first)")

        wheel_file = wheel_files[0]
        wheel_name = wheel_file.name

        # Transfer wheel to VM (preserve filename)
        print(f"[{vm_name}] Transferring wheel...")
        subprocess.run(
            ["multipass", "transfer", str(wheel_file), f"{vm_name}:/tmp/{wheel_name}"],
            capture_output=True,
            timeout=30
        )

        # Create venv and install
        print(f"[{vm_name}] Installing via pip...")
        result = multipass_exec(
            vm_name,
            f"python3 -m venv /tmp/venv && /tmp/venv/bin/pip install /tmp/{wheel_name}",
            timeout=60
        )

        assert result.returncode == 0, f"Failed to install wheel: {result.stderr}"

        # Test installed CLI
        result = multipass_exec(
            vm_name,
            "/tmp/venv/bin/redoubt --version",
            timeout=10
        )

        assert result.returncode == 0, f"Failed to run installed CLI: {result.stderr}"
        assert "0.1.0" in result.stdout, "Version output incorrect"

        print(f"[{vm_name}] ✅ pip installation works correctly")

    @pytest.mark.slow
    @pytest.mark.integration
    def test_pipx_install(self, ubuntu_vm):
        """Test installation via pipx."""
        vm_name = ubuntu_vm

        # Install pipx
        print(f"\n[{vm_name}] Installing pipx...")
        result = multipass_exec(
            vm_name,
            "sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv && python3 -m pip install --user pipx && python3 -m pipx ensurepath",
            timeout=300
        )

        if result.returncode != 0:
            pytest.skip(f"Failed to install pipx: {result.stderr}")

        # Check for built wheel
        wheel_files = list((REPO_ROOT / "dist").glob("*.whl"))
        if not wheel_files:
            pytest.skip("No wheel file to test")

        wheel_file = wheel_files[0]
        wheel_name = wheel_file.name

        # Transfer wheel to VM (preserve filename)
        subprocess.run(
            ["multipass", "transfer", str(wheel_file), f"{vm_name}:/tmp/{wheel_name}"],
            capture_output=True,
            timeout=30
        )

        # Install via pipx
        print(f"[{vm_name}] Installing via pipx...")
        result = multipass_exec(
            vm_name,
            f"/home/ubuntu/.local/bin/pipx install /tmp/{wheel_name}",
            timeout=60
        )

        assert result.returncode == 0, f"Failed to install with pipx: {result.stderr}"

        # Test installed CLI
        result = multipass_exec(
            vm_name,
            "/home/ubuntu/.local/bin/redoubt --version",
            timeout=10
        )

        assert result.returncode == 0, f"Failed to run pipx-installed CLI: {result.stderr}"
        print(f"[{vm_name}] ✅ pipx installation works correctly")


class TestDirectPyzInstallation:
    """Test direct .pyz installation and execution."""

    @pytest.mark.slow
    @pytest.mark.integration
    def test_pyz_on_ubuntu(self, ubuntu_vm):
        """Test .pyz works on fresh Ubuntu."""
        vm_name = ubuntu_vm

        # Ensure Python is installed
        print(f"\n[{vm_name}] Installing Python...")
        result = multipass_exec(
            vm_name,
            "sudo apt-get update && sudo apt-get install -y python3",
            timeout=300
        )

        if result.returncode != 0:
            pytest.skip(f"Failed to install Python: {result.stderr}")

        # Check for .pyz
        pyz_file = REPO_ROOT / "dist" / "provenance-demo.pyz"
        if not pyz_file.exists():
            pytest.skip("No .pyz file to test (run build first)")

        # Transfer .pyz to VM
        print(f"[{vm_name}] Transferring .pyz...")
        subprocess.run(
            ["multipass", "transfer", str(pyz_file), f"{vm_name}:/tmp/provenance-demo.pyz"],
            capture_output=True,
            timeout=30
        )

        # Test execution
        print(f"[{vm_name}] Testing .pyz execution...")

        # Test with python3
        result = multipass_exec(
            vm_name,
            "python3 /tmp/provenance-demo.pyz --version",
            timeout=10
        )
        assert result.returncode == 0, f"Failed to run with python3: {result.stderr}"

        # Test as executable
        result = multipass_exec(
            vm_name,
            "chmod +x /tmp/provenance-demo.pyz && /tmp/provenance-demo.pyz --version",
            timeout=10
        )
        assert result.returncode == 0, f"Failed to run as executable: {result.stderr}"

        # Test actual functionality
        result = multipass_exec(
            vm_name,
            "/tmp/provenance-demo.pyz hello World",
            timeout=10
        )
        assert result.returncode == 0, f"Failed to run with argument: {result.stderr}"
        assert "World" in result.stdout or "world" in result.stdout.lower(), "Greeting output incorrect"

        print(f"[{vm_name}] ✅ .pyz works correctly on Ubuntu")


class TestCrossPlatformCompatibility:
    """Test cross-platform compatibility."""

    @pytest.mark.slow
    @pytest.mark.integration
    def test_python_version_compatibility(self, ubuntu_vm):
        """Test with different Python versions."""
        vm_name = ubuntu_vm

        pyz_file = REPO_ROOT / "dist" / "provenance-demo.pyz"
        if not pyz_file.exists():
            pytest.skip("No .pyz file to test")

        # Transfer .pyz
        subprocess.run(
            ["multipass", "transfer", str(pyz_file), f"{vm_name}:/tmp/provenance-demo.pyz"],
            capture_output=True,
            timeout=30
        )

        # Test with Python 3.11+
        print(f"\n[{vm_name}] Installing multiple Python versions...")
        multipass_exec(
            vm_name,
            "sudo apt-get update && sudo apt-get install -y software-properties-common && sudo add-apt-repository -y ppa:deadsnakes/ppa && sudo apt-get update",
            timeout=300
        )

        # Test available Python versions
        for python_version in ["python3.11", "python3.12"]:
            print(f"[{vm_name}] Testing with {python_version}...")

            # Install Python version
            install_result = multipass_exec(
                vm_name,
                f"sudo apt-get install -y {python_version}",
                timeout=120
            )

            if install_result.returncode != 0:
                print(f"[{vm_name}] ⚠️  {python_version} not available, skipping")
                continue

            # Test with this version
            result = multipass_exec(
                vm_name,
                f"{python_version} /tmp/provenance-demo.pyz --version",
                timeout=10
            )

            assert result.returncode == 0, f"Failed with {python_version}: {result.stderr}"
            print(f"[{vm_name}] ✅ Works with {python_version}")


class TestEndToEndVerification:
    """Test end-to-end installation with verification."""

    @pytest.mark.slow
    @pytest.mark.integration
    def test_install_and_verify_attestation(self, ubuntu_vm):
        """Test installation and attestation verification."""
        vm_name = ubuntu_vm

        # Install gh CLI
        print(f"\n[{vm_name}] Installing GitHub CLI...")
        result = multipass_exec(
            vm_name,
            "curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && "
            "echo 'deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main' | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null && "
            "sudo apt-get update && sudo apt-get install -y gh",
            timeout=300
        )

        if result.returncode != 0:
            pytest.skip(f"Failed to install gh CLI: {result.stderr}")

        # For now, verify gh is working
        result = multipass_exec(vm_name, "gh version", timeout=10)
        assert result.returncode == 0, "gh CLI not working"

        print(f"[{vm_name}] ✅ GitHub CLI installed for verification")

        # Note: Actual attestation verification requires published release
        # We document that users should verify with:
        # gh attestation verify artifact.pyz --repo OWNER/REPO


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
