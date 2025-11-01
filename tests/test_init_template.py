#!/usr/bin/env python3
"""
Unit tests for scripts/init-template.py

Tests the template initialization wizard's core functionality:
- Configuration detection
- Validation functions
- File replacement logic
- Idempotency checking
"""

import re
import sys
from pathlib import Path
from typing import Dict
import pytest

# Add scripts directory to path to import init-template module
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

# Import functions from init-template.py
import importlib.util
spec = importlib.util.spec_from_file_location("init_template", REPO_ROOT / "scripts" / "init-template.py")
init_template = importlib.util.module_from_spec(spec)
spec.loader.exec_module(init_template)


class TestConfigurationDetection:
    """Test configuration detection from pyproject.toml."""

    def test_detect_package_name(self, tmp_path):
        """Test extracting package name from pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('''[project]
name = "my-awesome-package"
description = "A test package"
''')

        # Temporarily override REPO_ROOT
        original_root = init_template.REPO_ROOT
        init_template.REPO_ROOT = tmp_path

        try:
            config = init_template.detect_current_config()
            assert config["package_name"] == "my-awesome-package"
        finally:
            init_template.REPO_ROOT = original_root

    def test_detect_cli_command(self, tmp_path):
        """Test extracting CLI command from pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('''[project]
name = "my-package"

[project.scripts]
my-cli = "my_package.cli:main"
''')

        original_root = init_template.REPO_ROOT
        init_template.REPO_ROOT = tmp_path

        try:
            config = init_template.detect_current_config()
            assert config["cli_command"] == "my-cli"
        finally:
            init_template.REPO_ROOT = original_root

    def test_detect_repo_info(self, tmp_path):
        """Test extracting repository owner and name from URLs."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('''[project]
name = "my-package"

[project.urls]
Homepage = "https://github.com/myorg/myrepo"
''')

        original_root = init_template.REPO_ROOT
        init_template.REPO_ROOT = tmp_path

        try:
            config = init_template.detect_current_config()
            assert config["repo_owner"] == "myorg"
            assert config["repo_name"] == "myrepo"
        finally:
            init_template.REPO_ROOT = original_root

    def test_detect_description(self, tmp_path):
        """Test extracting description from pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('''[project]
name = "my-package"
description = "My awesome CLI tool"
''')

        original_root = init_template.REPO_ROOT
        init_template.REPO_ROOT = tmp_path

        try:
            config = init_template.detect_current_config()
            assert config["description"] == "My awesome CLI tool"
        finally:
            init_template.REPO_ROOT = original_root


class TestValidation:
    """Test validation functions for package names and CLI commands."""

    # Package name validation tests
    def test_validate_package_name_valid_lowercase(self):
        """Test valid lowercase package names."""
        assert init_template.validate_package_name("mypackage") is True
        assert init_template.validate_package_name("my_package") is True
        assert init_template.validate_package_name("_private") is True
        assert init_template.validate_package_name("package123") is True

    def test_validate_package_name_invalid_uppercase(self):
        """Test that uppercase package names are rejected."""
        assert init_template.validate_package_name("MyPackage") is False
        assert init_template.validate_package_name("PACKAGE") is False

    def test_validate_package_name_invalid_hyphen(self):
        """Test that hyphens in package names are rejected."""
        assert init_template.validate_package_name("my-package") is False

    def test_validate_package_name_invalid_start(self):
        """Test that package names starting with numbers are rejected."""
        assert init_template.validate_package_name("123package") is False

    def test_validate_package_name_invalid_chars(self):
        """Test that special characters are rejected."""
        assert init_template.validate_package_name("my.package") is False
        assert init_template.validate_package_name("my-package!") is False
        assert init_template.validate_package_name("my package") is False

    # CLI command validation tests
    def test_validate_cli_command_valid_lowercase(self):
        """Test valid CLI command names."""
        assert init_template.validate_cli_command("mycli") is True
        assert init_template.validate_cli_command("my-cli") is True
        assert init_template.validate_cli_command("cli123") is True

    def test_validate_cli_command_invalid_uppercase(self):
        """Test that uppercase CLI commands are rejected."""
        assert init_template.validate_cli_command("MyCLI") is False
        assert init_template.validate_cli_command("CLI") is False

    def test_validate_cli_command_invalid_start(self):
        """Test that CLI commands starting with numbers or hyphens are rejected."""
        assert init_template.validate_cli_command("123cli") is False
        assert init_template.validate_cli_command("-cli") is False

    def test_validate_cli_command_invalid_chars(self):
        """Test that special characters (except hyphens) are rejected."""
        assert init_template.validate_cli_command("my_cli") is False
        assert init_template.validate_cli_command("my.cli") is False
        assert init_template.validate_cli_command("my cli") is False


class TestFileReplacement:
    """Test file replacement functionality."""

    def test_replace_in_file_basic(self, tmp_path):
        """Test basic text replacement in a file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello OWNER, welcome to REPO_NAME!")

        replacements = {
            "OWNER": "myorg",
            "REPO_NAME": "myrepo"
        }

        modified = init_template.replace_in_file(test_file, replacements)

        assert modified is True
        assert test_file.read_text() == "Hello myorg, welcome to myrepo!"

    def test_replace_in_file_no_changes(self, tmp_path):
        """Test that files without matching text are not modified."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello world!")

        replacements = {
            "OWNER": "myorg",
            "REPO_NAME": "myrepo"
        }

        modified = init_template.replace_in_file(test_file, replacements)

        assert modified is False
        assert test_file.read_text() == "Hello world!"

    def test_replace_in_file_multiple_occurrences(self, tmp_path):
        """Test replacing multiple occurrences in a file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("demo demo demo")

        replacements = {"demo": "mycli"}

        modified = init_template.replace_in_file(test_file, replacements)

        assert modified is True
        assert test_file.read_text() == "mycli mycli mycli"

    def test_replace_in_file_nonexistent(self, tmp_path):
        """Test that nonexistent files return False."""
        test_file = tmp_path / "nonexistent.txt"

        replacements = {"old": "new"}

        modified = init_template.replace_in_file(test_file, replacements)

        assert modified is False


class TestIdempotency:
    """Test idempotency checking."""

    def test_is_customized_with_defaults(self, tmp_path):
        """Test that template with default values is detected as not customized."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('''[project]
name = "provenance-demo"
description = "Demo Secure CLI — reproducible & attestable release example"

[project.scripts]
demo = "demo_cli.cli:main"

[project.urls]
Homepage = "https://github.com/OWNER/provenance-template"
''')

        original_root = init_template.REPO_ROOT
        init_template.REPO_ROOT = tmp_path

        try:
            customized, unchanged = init_template.is_customized()
            assert customized is False
            assert "package_name" in unchanged
            assert "cli_command" in unchanged
            assert "repo_owner" in unchanged
            assert "repo_name" in unchanged
        finally:
            init_template.REPO_ROOT = original_root

    def test_is_customized_with_custom_values(self, tmp_path):
        """Test that customized template is detected correctly."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('''[project]
name = "my_awesome_cli"
description = "My Awesome CLI Tool"

[project.scripts]
mycli = "my_awesome_cli.cli:main"

[project.urls]
Homepage = "https://github.com/myorg/myrepo"
''')

        original_root = init_template.REPO_ROOT
        init_template.REPO_ROOT = tmp_path

        try:
            customized, unchanged = init_template.is_customized()
            assert customized is True
            assert len(unchanged) == 0
        finally:
            init_template.REPO_ROOT = original_root

    def test_is_customized_partially_customized(self, tmp_path):
        """Test detection of partially customized template."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('''[project]
name = "my_cli"
description = "Demo Secure CLI — reproducible & attestable release example"

[project.scripts]
demo = "my_cli.cli:main"

[project.urls]
Homepage = "https://github.com/OWNER/provenance-template"
''')

        original_root = init_template.REPO_ROOT
        init_template.REPO_ROOT = tmp_path

        try:
            customized, unchanged = init_template.is_customized()
            assert customized is False
            # Should detect that description, cli_command, repo_owner, repo_name are still defaults
            assert "description" in unchanged or "cli_command" in unchanged
        finally:
            init_template.REPO_ROOT = original_root


class TestPackageDirectoryRenaming:
    """Test package directory renaming functionality."""

    def test_rename_package_directory(self, tmp_path):
        """Test renaming package directory."""
        # Create old directory structure
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        old_dir = src_dir / "old_package"
        old_dir.mkdir()
        (old_dir / "__init__.py").write_text("# Old package")

        original_root = init_template.REPO_ROOT
        init_template.REPO_ROOT = tmp_path

        try:
            init_template.rename_package_directory("old_package", "new_package")

            # Check old directory is gone
            assert not old_dir.exists()

            # Check new directory exists with same content
            new_dir = src_dir / "new_package"
            assert new_dir.exists()
            assert (new_dir / "__init__.py").exists()
            assert (new_dir / "__init__.py").read_text() == "# Old package"
        finally:
            init_template.REPO_ROOT = original_root

    def test_rename_package_directory_no_op(self, tmp_path):
        """Test that renaming to same name is a no-op."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        package_dir = src_dir / "my_package"
        package_dir.mkdir()
        (package_dir / "__init__.py").write_text("# Package")

        original_root = init_template.REPO_ROOT
        init_template.REPO_ROOT = tmp_path

        try:
            # Should not raise any errors
            init_template.rename_package_directory("my_package", "my_package")

            # Directory should still exist
            assert package_dir.exists()
            assert (package_dir / "__init__.py").exists()
        finally:
            init_template.REPO_ROOT = original_root


class TestPromptWithDefault:
    """Test prompt_with_default function."""

    def test_prompt_with_default_accepts_empty(self, monkeypatch):
        """Test that empty input returns default value."""
        monkeypatch.setattr('builtins.input', lambda _: "")

        result = init_template.prompt_with_default("Test prompt", "default_value", required=False)
        assert result == "default_value"

    def test_prompt_with_default_accepts_input(self, monkeypatch):
        """Test that non-empty input is returned."""
        monkeypatch.setattr('builtins.input', lambda _: "user_value")

        result = init_template.prompt_with_default("Test prompt", "default_value", required=False)
        assert result == "user_value"

    def test_prompt_with_default_strips_whitespace(self, monkeypatch):
        """Test that input is stripped of whitespace."""
        monkeypatch.setattr('builtins.input', lambda _: "  user_value  ")

        result = init_template.prompt_with_default("Test prompt", "default_value", required=False)
        assert result == "user_value"


class TestDefaultValues:
    """Test that default placeholder values are correctly defined."""

    def test_default_values_exist(self):
        """Test that all expected default values are defined."""
        assert "package_name" in init_template.DEFAULT_VALUES
        assert "cli_command" in init_template.DEFAULT_VALUES
        assert "repo_owner" in init_template.DEFAULT_VALUES
        assert "repo_name" in init_template.DEFAULT_VALUES
        assert "project_name" in init_template.DEFAULT_VALUES
        assert "description" in init_template.DEFAULT_VALUES

    def test_default_values_correct(self):
        """Test that default values match template placeholders."""
        assert init_template.DEFAULT_VALUES["package_name"] == "provenance-demo"
        assert init_template.DEFAULT_VALUES["cli_command"] == "demo"
        assert init_template.DEFAULT_VALUES["repo_owner"] == "OWNER"
        assert init_template.DEFAULT_VALUES["repo_name"] == "provenance-template"


class TestColoredOutput:
    """Test colored output helper functions."""

    def test_colored_adds_color_codes(self):
        """Test that colored function adds ANSI color codes."""
        result = init_template.colored("test", init_template.Colors.GREEN)
        assert result.startswith("\033[")
        assert result.endswith("\033[0m")
        assert "test" in result

    def test_print_functions_exist(self):
        """Test that print helper functions exist."""
        # These should not raise AttributeError
        assert callable(init_template.print_header)
        assert callable(init_template.print_success)
        assert callable(init_template.print_warning)
        assert callable(init_template.print_error)
        assert callable(init_template.print_info)


class TestGitHubSecretsHelpers:
    """Test GitHub secrets helper functions."""

    def test_check_gh_cli_installed(self, monkeypatch):
        """Test detecting when gh CLI is installed."""
        import subprocess

        def mock_run(*args, **kwargs):
            class Result:
                returncode = 0
            return Result()

        monkeypatch.setattr(subprocess, "run", mock_run)
        assert init_template.check_gh_cli() is True

    def test_check_gh_cli_not_installed(self, monkeypatch):
        """Test detecting when gh CLI is not installed."""
        import subprocess

        def mock_run(*args, **kwargs):
            raise FileNotFoundError()

        monkeypatch.setattr(subprocess, "run", mock_run)
        assert init_template.check_gh_cli() is False

    def test_list_github_secrets_success(self, monkeypatch):
        """Test listing GitHub secrets successfully."""
        import subprocess

        def mock_run(*args, **kwargs):
            class Result:
                returncode = 0
                stdout = "PYPI_API_TOKEN\t2024-01-01\nHOMEBREW_TAP_TOKEN\t2024-01-02\n"
            return Result()

        monkeypatch.setattr(subprocess, "run", mock_run)
        secrets = init_template.list_github_secrets()

        assert secrets is not None
        assert len(secrets) == 2
        assert "PYPI_API_TOKEN" in secrets
        assert "HOMEBREW_TAP_TOKEN" in secrets

    def test_list_github_secrets_failure(self, monkeypatch):
        """Test when listing secrets fails."""
        import subprocess

        def mock_run(*args, **kwargs):
            class Result:
                returncode = 1
                stdout = ""
            return Result()

        monkeypatch.setattr(subprocess, "run", mock_run)
        secrets = init_template.list_github_secrets()

        assert secrets is None

    def test_list_github_secrets_no_secrets(self, monkeypatch):
        """Test listing secrets when none exist."""
        import subprocess

        def mock_run(*args, **kwargs):
            class Result:
                returncode = 0
                stdout = ""
            return Result()

        monkeypatch.setattr(subprocess, "run", mock_run)
        secrets = init_template.list_github_secrets()

        assert secrets is not None
        assert len(secrets) == 0

    def test_list_github_secrets_not_installed(self, monkeypatch):
        """Test listing secrets when gh CLI is not installed."""
        import subprocess

        def mock_run(*args, **kwargs):
            raise FileNotFoundError()

        monkeypatch.setattr(subprocess, "run", mock_run)
        secrets = init_template.list_github_secrets()

        assert secrets is None


class TestSecretsConfigurationFlow:
    """Test secrets configuration workflow (integration-style tests)."""

    def test_configure_secrets_gh_not_installed(self, monkeypatch, capsys):
        """Test secrets config when gh CLI is not installed."""
        monkeypatch.setattr(init_template, "check_gh_cli", lambda: False)

        config = {"package_name": "test_pkg"}
        init_template.configure_github_secrets(config)

        captured = capsys.readouterr()
        assert "GitHub CLI (gh) is not installed" in captured.out
        assert "brew install gh" in captured.out

    def test_configure_secrets_not_authenticated(self, monkeypatch, capsys):
        """Test secrets config when not authenticated."""
        import subprocess

        monkeypatch.setattr(init_template, "check_gh_cli", lambda: True)

        def mock_run(cmd, **kwargs):
            if "auth" in cmd:
                class Result:
                    returncode = 1
                return Result()
            return None

        monkeypatch.setattr(subprocess, "run", mock_run)

        config = {"package_name": "test_pkg"}
        init_template.configure_github_secrets(config)

        captured = capsys.readouterr()
        assert "Not authenticated with GitHub CLI" in captured.out
        assert "gh auth login" in captured.out


# End-to-end integration tests
class TestEndToEndScenario:
    """
    End-to-end integration tests for the init wizard.

    These test the full workflow:
    1. Create a temporary copy of template files
    2. Run wizard functions with mocked inputs
    3. Verify all files were updated correctly
    4. Verify package directory was renamed
    5. Verify idempotency (running again detects custom config)
    6. Verify secrets configuration flow (without affecting real GitHub)
    """

    def create_test_repository(self, tmp_path):
        """Create a minimal test repository structure."""
        # Create pyproject.toml
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('''[project]
name = "provenance-demo"
version = "0.1.0"
description = "Demo Secure CLI — reproducible & attestable release example"

[project.scripts]
demo = "demo_cli.cli:main"

[project.urls]
Homepage = "https://github.com/OWNER/provenance-template"
''')

        # Create src directory with package
        src_dir = tmp_path / "src" / "demo_cli"
        src_dir.mkdir(parents=True)
        (src_dir / "__init__.py").write_text("# Demo package")
        (src_dir / "cli.py").write_text('def main():\n    print("demo")\n')

        # Create docs directory
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "README.md").write_text("# Documentation\n\nFor demo package.")

        # Create workflow directory
        workflows_dir = tmp_path / ".github" / "workflows"
        workflows_dir.mkdir(parents=True)
        (workflows_dir / "release.yml").write_text("name: Release\n# OWNER/provenance-template")

        # Create README
        readme = tmp_path / "README.md"
        readme.write_text("# Demo CLI\n\nRepository: OWNER/provenance-template\nCommand: demo")

        return tmp_path

    def test_full_wizard_flow(self, tmp_path):
        """Test the complete wizard flow with all components."""
        # Setup test repository
        repo = self.create_test_repository(tmp_path)

        # Override REPO_ROOT
        original_root = init_template.REPO_ROOT
        init_template.REPO_ROOT = repo

        try:
            # Step 1: Detect current config (should be defaults)
            config = init_template.detect_current_config()
            assert config["package_name"] == "provenance-demo"
            assert config["cli_command"] == "demo"
            assert config["repo_owner"] == "OWNER"

            # Step 2: Create new configuration
            new_config = {
                "package_name": "my_secure_cli",
                "cli_command": "secure-cli",
                "repo_owner": "myorg",
                "repo_name": "my-project",
                "project_name": "My Secure CLI",
                "description": "A secure CLI tool",
                "author": "Test Author",
                "author_email": "test@example.com"
            }

            # Step 3: Apply configuration
            init_template.apply_configuration(new_config)

            # Step 4: Verify files were updated
            pyproject = (repo / "pyproject.toml").read_text()
            assert "my-secure-cli" in pyproject
            assert "A secure CLI tool" in pyproject

            readme = (repo / "README.md").read_text()
            assert "myorg/my-project" in readme
            assert "secure-cli" in readme

            # Step 5: Verify package directory was renamed
            assert (repo / "src" / "my_secure_cli").exists()
            assert not (repo / "src" / "demo_cli").exists()

            # Step 6: Verify idempotency - detect new config
            new_detected = init_template.detect_current_config()
            assert new_detected["package_name"] == "my-secure-cli"
            assert new_detected["repo_owner"] == "myorg"

        finally:
            init_template.REPO_ROOT = original_root

    def test_partial_configuration_update(self, tmp_path):
        """Test updating only some values (idempotent update)."""
        repo = self.create_test_repository(tmp_path)

        original_root = init_template.REPO_ROOT
        init_template.REPO_ROOT = repo

        try:
            # First update: Change package name only
            config1 = {
                "package_name": "first_cli",
                "cli_command": "demo",  # Keep original
                "repo_owner": "OWNER",  # Keep original
                "repo_name": "provenance-template",
                "description": "Demo Secure CLI — reproducible & attestable release example",
            }
            init_template.apply_configuration(config1)

            # Verify first update
            assert (repo / "src" / "first_cli").exists()

            # Second update: Change repo owner only
            config2 = {
                "package_name": "first_cli",  # Keep from first update
                "cli_command": "demo",
                "repo_owner": "neworg",  # Change this
                "repo_name": "provenance-template",
                "description": "Demo Secure CLI — reproducible & attestable release example",
            }
            init_template.apply_configuration(config2)

            # Verify second update didn't break things
            assert (repo / "src" / "first_cli").exists()
            readme = (repo / "README.md").read_text()
            assert "neworg/provenance-template" in readme

        finally:
            init_template.REPO_ROOT = original_root

    def test_file_update_coverage(self, tmp_path):
        """Test that all expected file types are updated."""
        repo = self.create_test_repository(tmp_path)

        # Add more file types
        (repo / "CHANGELOG.md").write_text("# Changelog\n\ndemo-cli changes")
        packaging_dir = repo / "packaging" / "homebrew"
        packaging_dir.mkdir(parents=True)
        (packaging_dir / "formula.rb").write_text('class Demo < Formula\n  url "github.com/OWNER/provenance-template"\nend')

        original_root = init_template.REPO_ROOT
        init_template.REPO_ROOT = repo

        try:
            config = {
                "package_name": "test_cli",
                "cli_command": "test",
                "repo_owner": "testorg",
                "repo_name": "test-repo",
                "description": "Test CLI",
            }
            init_template.apply_configuration(config)

            # Verify different file types were updated
            assert "test-cli" in (repo / "pyproject.toml").read_text()
            assert "testorg/test-repo" in (repo / "README.md").read_text()
            assert "test-cli" in (repo / "CHANGELOG.md").read_text()
            assert "testorg/test-repo" in (packaging_dir / "formula.rb").read_text()

        finally:
            init_template.REPO_ROOT = original_root

    def test_directory_rename_edge_cases(self, tmp_path):
        """Test directory renaming edge cases."""
        repo = self.create_test_repository(tmp_path)

        original_root = init_template.REPO_ROOT
        init_template.REPO_ROOT = repo

        try:
            # Test 1: Normal rename
            init_template.rename_package_directory("demo_cli", "new_cli")
            assert (repo / "src" / "new_cli").exists()
            assert not (repo / "src" / "demo_cli").exists()

            # Test 2: Rename to same name (no-op)
            init_template.rename_package_directory("new_cli", "new_cli")
            assert (repo / "src" / "new_cli").exists()

            # Test 3: Source doesn't exist (should handle gracefully)
            init_template.rename_package_directory("nonexistent", "something")
            # Should not crash, just log warning

            # Test 4: Target already exists
            (repo / "src" / "existing").mkdir()
            init_template.rename_package_directory("new_cli", "existing")
            # Should not crash, existing directory remains
            assert (repo / "src" / "existing").exists()
            assert (repo / "src" / "new_cli").exists()

        finally:
            init_template.REPO_ROOT = original_root

    def test_secrets_configuration_mock_flow(self, monkeypatch, capsys):
        """Test secrets configuration flow without touching real GitHub."""
        import subprocess

        # Mock all GitHub CLI interactions
        call_log = []

        def mock_run(cmd, **kwargs):
            call_log.append((" ".join(cmd), kwargs))

            if "auth" in cmd and "status" in cmd:
                class AuthResult:
                    returncode = 0
                    stdout = "Logged in to github.com"
                    stderr = ""
                return AuthResult()

            if "secret" in cmd and "list" in cmd:
                class ListResult:
                    returncode = 0
                    stdout = "PYPI_API_TOKEN\tUpdated 2024-01-01\nHOMEBREW_TAP_TOKEN\tUpdated 2024-01-01"
                    stderr = ""
                return ListResult()

            if "secret" in cmd and "set" in cmd:
                class SetResult:
                    returncode = 0
                    stdout = ""
                    stderr = ""
                return SetResult()

            class DefaultResult:
                returncode = 0
                stdout = ""
                stderr = ""
            return DefaultResult()

        monkeypatch.setattr(subprocess, "run", mock_run)
        monkeypatch.setattr(init_template, "check_gh_cli", lambda: True)

        # Mock user input for platform selection
        inputs = iter(["skip"])  # User chooses to skip
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        config = {"package_name": "test_cli"}
        init_template.configure_github_secrets(config)

        # Verify gh CLI was checked
        assert any("auth" in cmd for cmd, _ in call_log)
        assert any("secret list" in cmd for cmd, _ in call_log)

        captured = capsys.readouterr()
        assert "Checking existing secrets" in captured.out
        assert "PYPI_API_TOKEN" in captured.out

    def test_error_handling_file_permissions(self, tmp_path):
        """Test error handling when files have permission issues."""
        repo = self.create_test_repository(tmp_path)

        original_root = init_template.REPO_ROOT
        init_template.REPO_ROOT = repo

        try:
            # Make a file read-only
            readme = repo / "README.md"
            readme.chmod(0o444)  # Read-only

            config = {
                "package_name": "test_cli",
                "cli_command": "test",
                "repo_owner": "testorg",
                "repo_name": "test-repo",
                "description": "Test",
            }

            # Should handle permission error gracefully
            init_template.apply_configuration(config)

            # Restore permissions
            readme.chmod(0o644)

        finally:
            init_template.REPO_ROOT = original_root

    def test_customization_detection(self, tmp_path):
        """Test detecting whether template is customized."""
        repo = self.create_test_repository(tmp_path)

        original_root = init_template.REPO_ROOT
        init_template.REPO_ROOT = repo

        try:
            # Should detect as uncustomized (uses default values)
            customized, unchanged = init_template.is_customized()
            assert not customized
            assert "repo_owner" in unchanged  # OWNER is default

            # Apply customization
            config = {
                "package_name": "custom_cli",
                "cli_command": "custom",
                "repo_owner": "customorg",
                "repo_name": "custom-repo",
                "description": "Custom description",
            }
            init_template.apply_configuration(config)

            # Should now detect as customized
            customized, unchanged = init_template.is_customized()
            assert customized
            assert len(unchanged) == 0

        finally:
            init_template.REPO_ROOT = original_root


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
