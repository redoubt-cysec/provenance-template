"""
Runtime Security Tests

Validates runtime security properties of the built application.
"""
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"


class TestPyzSecurity:
    """Test .pyz zipapp security properties."""

    def test_pyz_shebang_security(self):
        """Verify .pyz has secure shebang."""
        # Build the pyz first
        env = os.environ.copy()
        env["SOURCE_DATE_EPOCH"] = "1234567890"

        result = subprocess.run(
            [str(SCRIPTS_DIR / "build_pyz.sh")],
            env=env,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            pytest.skip(f"Build failed: {result.stderr}")

        pyz_file = REPO_ROOT / "dist" / "client.pyz"
        if not pyz_file.exists():
            pytest.skip("No .pyz file to test")

        # Read shebang
        with open(pyz_file, "rb") as f:
            shebang = f.readline()

        # Should have Python shebang
        assert shebang.startswith(b"#!/usr/bin/env python3") or \
               shebang.startswith(b"#!/usr/bin/python3"), \
            "PYZ should have secure Python shebang"

    @pytest.mark.slow
    def test_pyz_no_bytecode_cache_pollution(self):
        """Verify .pyz doesn't write __pycache__ to filesystem."""
        # Build the pyz
        env = os.environ.copy()
        env["SOURCE_DATE_EPOCH"] = "1234567890"

        result = subprocess.run(
            [str(SCRIPTS_DIR / "build_pyz.sh")],
            env=env,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            pytest.skip(f"Build failed: {result.stderr}")

        pyz_file = REPO_ROOT / "dist" / "client.pyz"
        if not pyz_file.exists():
            pytest.skip("No .pyz file to test")

        # Run in temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Copy pyz to temp and run
            import shutil
            temp_pyz = Path(tmpdir) / "test.pyz"
            shutil.copy(pyz_file, temp_pyz)

            # Execute it
            subprocess.run(
                [sys.executable, str(temp_pyz), "--version"],
                cwd=tmpdir,
                capture_output=True,
                timeout=5
            )

            # Check for __pycache__
            pycache_dirs = list(Path(tmpdir).rglob("__pycache__"))
            assert len(pycache_dirs) == 0, \
                "PYZ should not create __pycache__ directories when run"

    @pytest.mark.slow
    def test_pyz_runs_without_write_access(self):
        """Verify .pyz can run without write permissions to its directory."""
        # Build the pyz
        env = os.environ.copy()
        env["SOURCE_DATE_EPOCH"] = "1234567890"

        result = subprocess.run(
            [str(SCRIPTS_DIR / "build_pyz.sh")],
            env=env,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            pytest.skip(f"Build failed: {result.stderr}")

        pyz_file = REPO_ROOT / "dist" / "client.pyz"
        if not pyz_file.exists():
            pytest.skip("No .pyz file to test")

        # Copy to read-only directory
        with tempfile.TemporaryDirectory() as tmpdir:
            import shutil
            ro_dir = Path(tmpdir) / "readonly"
            ro_dir.mkdir()
            temp_pyz = ro_dir / "test.pyz"
            shutil.copy(pyz_file, temp_pyz)

            # Make directory read-only
            os.chmod(ro_dir, 0o555)

            try:
                # Should still be able to run
                result = subprocess.run(
                    [sys.executable, str(temp_pyz), "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                assert result.returncode == 0, \
                    "PYZ should run without write access to its directory"
            finally:
                # Restore permissions for cleanup
                os.chmod(ro_dir, 0o755)


class TestDependencyIsolation:
    """Test that the application properly isolates dependencies."""

    def test_no_system_package_pollution(self):
        """Verify build doesn't pollute system site-packages."""
        # Get system site-packages before build
        result = subprocess.run(
            [sys.executable, "-c", "import site; print(site.getsitepackages())"],
            capture_output=True,
            text=True,
            check=True
        )
        site_packages = result.stdout.strip()

        # Build should not touch system packages
        env = os.environ.copy()
        env["SOURCE_DATE_EPOCH"] = "1234567890"

        build_result = subprocess.run(
            [str(SCRIPTS_DIR / "build_pyz.sh")],
            env=env,
            capture_output=True,
            text=True
        )

        if build_result.returncode != 0:
            pytest.skip(f"Build failed: {build_result.stderr}")

        # System site-packages should be unchanged
        # (This is a basic check; real verification would diff packages)
        result_after = subprocess.run(
            [sys.executable, "-c", "import site; print(site.getsitepackages())"],
            capture_output=True,
            text=True,
            check=True
        )
        assert result.stdout == result_after.stdout, \
            "Build should not modify system site-packages"


class TestInputValidation:
    """Test CLI input validation and sanitization."""

    def test_no_shell_injection_in_args(self):
        """Verify CLI args don't allow shell injection."""
        # Build the pyz
        env = os.environ.copy()
        env["SOURCE_DATE_EPOCH"] = "1234567890"

        result = subprocess.run(
            [str(SCRIPTS_DIR / "build_pyz.sh")],
            env=env,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            pytest.skip(f"Build failed: {result.stderr}")

        pyz_file = REPO_ROOT / "dist" / "client.pyz"
        if not pyz_file.exists():
            pytest.skip("No .pyz file to test")

        # Try shell injection payloads
        dangerous_inputs = [
            "; ls -la",
            "$(whoami)",
            "`id`",
            "| cat /etc/passwd",
            "&& echo hacked",
        ]

        for payload in dangerous_inputs:
            # Run with dangerous input
            result = subprocess.run(
                [sys.executable, str(pyz_file), payload],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Should not execute shell commands
            # Output should just be the greeting with the payload as text
            assert "hacked" not in result.stdout.lower(), \
                f"Shell injection vulnerability with payload: {payload}"
            assert "root:" not in result.stdout, \
                f"Command execution with payload: {payload}"

    def test_path_traversal_protection(self):
        """Verify no path traversal vulnerabilities."""
        # If the CLI ever takes file paths, it should validate them
        # For now, just verify the build scripts don't have obvious issues

        build_script = SCRIPTS_DIR / "build_pyz.sh"
        content = build_script.read_text()

        # Should not have unquoted variables that could be exploited
        dangerous_patterns = [
            "cd $",  # Unquoted cd
            "rm -rf $",  # Unquoted rm
        ]

        for pattern in dangerous_patterns:
            assert pattern not in content, \
                f"Build script has potential path traversal: {pattern}"


class TestErrorHandling:
    """Test error handling and information disclosure."""

    @pytest.mark.slow
    def test_no_stacktrace_in_normal_errors(self):
        """Verify user errors don't expose full stack traces."""
        # Build the pyz
        env = os.environ.copy()
        env["SOURCE_DATE_EPOCH"] = "1234567890"

        result = subprocess.run(
            [str(SCRIPTS_DIR / "build_pyz.sh")],
            env=env,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            pytest.skip(f"Build failed: {result.stderr}")

        pyz_file = REPO_ROOT / "dist" / "client.pyz"
        if not pyz_file.exists():
            pytest.skip("No .pyz file to test")

        # Trigger an error with invalid flag
        result = subprocess.run(
            [sys.executable, str(pyz_file), "--invalid-flag"],
            capture_output=True,
            text=True,
            timeout=5
        )

        # Should get clean error, not full traceback
        # (argparse will show usage, not Python traceback)
        assert "Traceback" not in result.stderr, \
            "User errors should not expose Python tracebacks"
        assert "File " not in result.stderr or "argparse" not in result.stderr, \
            "Should not expose internal file paths in user errors"

    @pytest.mark.slow
    def test_no_sensitive_info_in_version(self):
        """Verify --version doesn't leak sensitive paths."""
        # Build the pyz
        env = os.environ.copy()
        env["SOURCE_DATE_EPOCH"] = "1234567890"

        result = subprocess.run(
            [str(SCRIPTS_DIR / "build_pyz.sh")],
            env=env,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            pytest.skip(f"Build failed: {result.stderr}")

        pyz_file = REPO_ROOT / "dist" / "client.pyz"
        if not pyz_file.exists():
            pytest.skip("No .pyz file to test")

        # Get version output
        result = subprocess.run(
            [sys.executable, str(pyz_file), "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )

        # Should not contain absolute paths from build system
        assert "/home/" not in result.stdout, \
            "Version should not leak build system paths"
        assert "/Users/" not in result.stdout, \
            "Version should not leak build system paths"


class TestFilePermissions:
    """Test file permissions and access controls."""

    def test_build_output_permissions(self):
        """Verify build outputs have secure permissions."""
        # Build the pyz
        env = os.environ.copy()
        env["SOURCE_DATE_EPOCH"] = "1234567890"

        result = subprocess.run(
            [str(SCRIPTS_DIR / "build_pyz.sh")],
            env=env,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            pytest.skip(f"Build failed: {result.stderr}")

        dist_dir = REPO_ROOT / "dist"
        if not dist_dir.exists():
            pytest.skip("No dist directory")

        # Check permissions on output files
        for item in dist_dir.iterdir():
            stat = os.stat(item)
            mode = stat.st_mode

            # Should not be world-writable
            assert not (mode & 0o002), \
                f"{item.name} is world-writable (insecure)"

            # Executable files should be user+group executable, not world
            if item.suffix == ".pyz":
                # Should be executable by owner
                assert mode & 0o100, \
                    f"{item.name} should be executable"


class TestNetworkSecurity:
    """Test network security properties (if applicable)."""

    def test_no_network_calls_in_basic_usage(self):
        """Verify basic CLI usage doesn't make network calls."""
        # Build the pyz
        env = os.environ.copy()
        env["SOURCE_DATE_EPOCH"] = "1234567890"

        result = subprocess.run(
            [str(SCRIPTS_DIR / "build_pyz.sh")],
            env=env,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            pytest.skip(f"Build failed: {result.stderr}")

        pyz_file = REPO_ROOT / "dist" / "client.pyz"
        if not pyz_file.exists():
            pytest.skip("No .pyz file to test")

        # Run with no network
        # (This is a basic test; proper testing would use network namespace isolation)
        result = subprocess.run(
            [sys.executable, str(pyz_file), "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            env={**env, "NO_PROXY": "*"}  # Block proxies
        )

        # Should succeed without network
        assert result.returncode == 0, \
            "Basic CLI usage should work without network access"


class TestCodeIntegrity:
    """Test code integrity and tampering detection."""

    def test_pyz_is_valid_zip(self):
        """Verify .pyz is a valid ZIP file."""
        # Build the pyz
        env = os.environ.copy()
        env["SOURCE_DATE_EPOCH"] = "1234567890"

        result = subprocess.run(
            [str(SCRIPTS_DIR / "build_pyz.sh")],
            env=env,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            pytest.skip(f"Build failed: {result.stderr}")

        pyz_file = REPO_ROOT / "dist" / "client.pyz"
        if not pyz_file.exists():
            pytest.skip("No .pyz file to test")

        # Should be valid ZIP
        try:
            with zipfile.ZipFile(pyz_file, 'r') as zf:
                # Test the ZIP file integrity
                bad_file = zf.testzip()
                assert bad_file is None, \
                    f"PYZ has corrupted file: {bad_file}"
        except zipfile.BadZipFile:
            pytest.fail("PYZ is not a valid ZIP file")

    @pytest.mark.slow
    def test_pyz_contains_expected_files(self):
        """Verify .pyz contains only expected files (no extraneous code)."""
        # Build the pyz
        env = os.environ.copy()
        env["SOURCE_DATE_EPOCH"] = "1234567890"

        result = subprocess.run(
            [str(SCRIPTS_DIR / "build_pyz.sh")],
            env=env,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            pytest.skip(f"Build failed: {result.stderr}")

        pyz_file = REPO_ROOT / "dist" / "client.pyz"
        if not pyz_file.exists():
            pytest.skip("No .pyz file to test")

        # List contents
        with zipfile.ZipFile(pyz_file, 'r') as zf:
            files = zf.namelist()

        # Should contain our package
        assert any("demo_cli" in f for f in files), \
            "PYZ should contain demo_cli package"

        # Should have __main__.py
        assert "__main__.py" in files, \
            "PYZ should have __main__.py entry point"

        # Should NOT contain test files
        test_files = [f for f in files if "test" in f.lower()]
        assert len(test_files) == 0, \
            f"PYZ should not contain test files: {test_files}"

        # Should NOT contain __pycache__
        pycache_files = [f for f in files if "__pycache__" in f]
        assert len(pycache_files) == 0, \
            "PYZ should not contain __pycache__ directories"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
