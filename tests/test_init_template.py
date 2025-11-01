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
name = "demo_cli"
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
        assert init_template.DEFAULT_VALUES["package_name"] == "demo_cli"
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


# Integration test placeholder
class TestEndToEndScenario:
    """
    End-to-end integration tests would go here.

    These would test the full workflow:
    1. Create a temporary copy of the template
    2. Run the init wizard with mocked inputs
    3. Verify all files were updated correctly
    4. Verify package directory was renamed
    5. Verify the result is idempotent (running again detects custom config)
    6. Verify secrets configuration flow

    Note: These are more complex and would require mocking user input
    and potentially running the full script in a subprocess.
    """

    def test_integration_placeholder(self):
        """Placeholder for integration tests."""
        # TODO: Implement full end-to-end integration test
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
