#!/usr/bin/env python3
"""
Provenance Template Initialization Wizard

This script helps you customize the provenance-template for your own project.
It's idempotent - safe to run multiple times.

Usage:
    python scripts/init-template.py

What it does:
- Renames the package (demo_cli → your_package)
- Updates CLI command name (demo → your-command)
- Replaces placeholders (OWNER, repository name)
- Configures project metadata
- Optionally enables/disables distribution platforms
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def colored(text: str, color: str) -> str:
    """Add color to text."""
    return f"{color}{text}{Colors.END}"

def print_header(text: str) -> None:
    """Print a section header."""
    print("\n" + "=" * 70)
    print(colored(text, Colors.HEADER + Colors.BOLD))
    print("=" * 70 + "\n")

def print_success(text: str) -> None:
    """Print success message."""
    print(colored(f"✓ {text}", Colors.GREEN))

def print_warning(text: str) -> None:
    """Print warning message."""
    print(colored(f"⚠ {text}", Colors.YELLOW))

def print_error(text: str) -> None:
    """Print error message."""
    print(colored(f"✗ {text}", Colors.RED))

def print_info(text: str) -> None:
    """Print info message."""
    print(colored(f"ℹ {text}", Colors.CYAN))

# Repository root
REPO_ROOT = Path(__file__).parent.parent.resolve()

# Default/placeholder values to detect
DEFAULT_VALUES = {
    "package_name": "demo_cli",
    "cli_command": "demo",
    "repo_owner": "OWNER",
    "repo_name": "provenance-template",
    "project_name": "Provenance Demo",
    "description": "Demo Secure CLI — reproducible & attestable release example",
}

def detect_current_config() -> Dict[str, str]:
    """Detect current configuration from pyproject.toml."""
    pyproject_path = REPO_ROOT / "pyproject.toml"

    if not pyproject_path.exists():
        print_error("pyproject.toml not found!")
        sys.exit(1)

    content = pyproject_path.read_text()

    config = {}

    # Extract package name
    if match := re.search(r'name\s*=\s*"([^"]+)"', content):
        config["package_name"] = match.group(1)

    # Extract description
    if match := re.search(r'description\s*=\s*"([^"]+)"', content):
        config["description"] = match.group(1)

    # Extract CLI command from scripts section
    if match := re.search(r'\[project\.scripts\]\s*([a-z][a-z0-9-]*)\s*=', content):
        config["cli_command"] = match.group(1)

    # Try to detect repo owner/name from URLs
    if match := re.search(r'github\.com/([^/]+)/([^/"]+)', content):
        config["repo_owner"] = match.group(1)
        config["repo_name"] = match.group(2)

    return config

def is_customized() -> Tuple[bool, List[str]]:
    """Check if template has been customized."""
    config = detect_current_config()
    unchanged = []

    for key, default_value in DEFAULT_VALUES.items():
        if key in config and config[key] == default_value:
            unchanged.append(key)

    return (len(unchanged) == 0, unchanged)

def prompt_with_default(prompt_text: str, default: str, required: bool = True) -> str:
    """Prompt user for input with a default value."""
    while True:
        user_input = input(f"{prompt_text} [{default}]: ").strip()

        if not user_input:
            if required and not default:
                print_warning("This field is required.")
                continue
            return default

        return user_input

def validate_package_name(name: str) -> bool:
    """Validate Python package name."""
    # Must be valid Python identifier
    if not re.match(r'^[a-z_][a-z0-9_]*$', name):
        print_error("Package name must be lowercase, start with letter/underscore, contain only letters/numbers/underscores")
        return False
    return True

def validate_cli_command(name: str) -> bool:
    """Validate CLI command name."""
    # Can contain hyphens, must be lowercase
    if not re.match(r'^[a-z][a-z0-9-]*$', name):
        print_error("CLI command must be lowercase, start with letter, contain only letters/numbers/hyphens")
        return False
    return True

def get_project_config() -> Dict[str, str]:
    """Interactively gather project configuration."""
    print_header("PROJECT CONFIGURATION")

    current = detect_current_config()

    print_info("Current configuration:")
    for key, value in current.items():
        default_marker = " (default)" if DEFAULT_VALUES.get(key) == value else ""
        print(f"  {key}: {value}{default_marker}")

    print("\nEnter new values (press Enter to keep current):\n")

    config = {}

    # Package name
    while True:
        default_package = current.get("package_name", DEFAULT_VALUES["package_name"])
        user_input = input(f"Python package name [{default_package}]: ").strip()

        if not user_input:
            package_name = default_package
            config["package_name"] = package_name
            break
        elif validate_package_name(user_input):
            config["package_name"] = user_input
            break

    # CLI command
    while True:
        default_cli = current.get("cli_command", DEFAULT_VALUES["cli_command"])
        user_input = input(f"CLI command name [{default_cli}]: ").strip()

        if not user_input:
            cli_command = default_cli
            config["cli_command"] = cli_command
            break
        elif validate_cli_command(user_input):
            config["cli_command"] = user_input
            break

    # Repository owner
    config["repo_owner"] = prompt_with_default(
        "GitHub repository owner/organization",
        current.get("repo_owner", DEFAULT_VALUES["repo_owner"])
    )

    # Repository name
    config["repo_name"] = prompt_with_default(
        "GitHub repository name",
        current.get("repo_name", DEFAULT_VALUES["repo_name"])
    )

    # Project name
    config["project_name"] = prompt_with_default(
        "Project display name",
        config["cli_command"].replace("-", " ").title()
    )

    # Description
    config["description"] = prompt_with_default(
        "Project description",
        current.get("description", DEFAULT_VALUES["description"])
    )

    # Author (optional)
    git_user = subprocess.run(
        ["git", "config", "user.name"],
        capture_output=True,
        text=True
    ).stdout.strip()

    config["author"] = prompt_with_default(
        "Author name (optional)",
        git_user,
        required=False
    )

    # Email (optional)
    git_email = subprocess.run(
        ["git", "config", "user.email"],
        capture_output=True,
        text=True
    ).stdout.strip()

    config["author_email"] = prompt_with_default(
        "Author email (optional)",
        git_email,
        required=False
    )

    return config

def confirm_changes(config: Dict[str, str]) -> bool:
    """Show summary and confirm changes."""
    print_header("CONFIGURATION SUMMARY")

    print("The following changes will be applied:\n")
    for key, value in config.items():
        if value:  # Only show non-empty values
            print(f"  {colored(key, Colors.BOLD)}: {value}")

    print("\nThis will update:")
    print("  • pyproject.toml")
    print("  • Source code directory structure")
    print("  • Documentation files")
    print("  • GitHub workflow files")
    print("  • Platform configuration files")

    print()
    response = input("Apply these changes? [y/N]: ").strip().lower()
    return response in ["y", "yes"]

def replace_in_file(file_path: Path, replacements: Dict[str, str]) -> bool:
    """Replace text in a file. Returns True if file was modified."""
    if not file_path.exists():
        return False

    content = file_path.read_text()
    original = content

    for old, new in replacements.items():
        content = content.replace(old, new)

    if content != original:
        file_path.write_text(content)
        return True

    return False

def rename_package_directory(old_name: str, new_name: str) -> None:
    """Rename the package directory."""
    old_path = REPO_ROOT / "src" / old_name
    new_path = REPO_ROOT / "src" / new_name

    if old_path.exists() and old_path != new_path:
        if new_path.exists():
            print_warning(f"Directory {new_path} already exists, skipping rename")
        else:
            old_path.rename(new_path)
            print_success(f"Renamed package directory: {old_name} → {new_name}")

def apply_configuration(config: Dict[str, str]) -> None:
    """Apply configuration changes across the repository."""
    print_header("APPLYING CHANGES")

    current = detect_current_config()

    # Build replacement map
    replacements = {}

    # Package name replacements
    if config["package_name"] != current.get("package_name"):
        replacements[current.get("package_name", DEFAULT_VALUES["package_name"])] = config["package_name"]
        replacements[current.get("package_name", DEFAULT_VALUES["package_name"]).replace("_", "-")] = config["package_name"].replace("_", "-")

    # CLI command replacements
    if config["cli_command"] != current.get("cli_command"):
        replacements[current.get("cli_command", DEFAULT_VALUES["cli_command"])] = config["cli_command"]

    # Repository owner/name replacements
    if config["repo_owner"] != current.get("repo_owner"):
        replacements[current.get("repo_owner", DEFAULT_VALUES["repo_owner"])] = config["repo_owner"]

    if config["repo_name"] != current.get("repo_name"):
        replacements[current.get("repo_name", DEFAULT_VALUES["repo_name"])] = config["repo_name"]

    # Description replacement
    if config["description"] != current.get("description"):
        replacements[current.get("description", DEFAULT_VALUES["description"])] = config["description"]

    # Files to update (in order of importance)
    files_to_update = [
        REPO_ROOT / "pyproject.toml",
        REPO_ROOT / "README.md",
        REPO_ROOT / "CHANGELOG.md",
    ]

    # Add all Python files in src/
    src_dir = REPO_ROOT / "src"
    if src_dir.exists():
        files_to_update.extend(src_dir.rglob("*.py"))

    # Add all documentation files
    docs_dir = REPO_ROOT / "docs"
    if docs_dir.exists():
        files_to_update.extend(docs_dir.rglob("*.md"))

    # Add workflow files
    workflows_dir = REPO_ROOT / ".github" / "workflows"
    if workflows_dir.exists():
        files_to_update.extend(workflows_dir.rglob("*.yml"))

    # Add platform config files
    packaging_dir = REPO_ROOT / "packaging"
    if packaging_dir.exists():
        files_to_update.extend(packaging_dir.rglob("*"))

    # Apply replacements
    modified_files = []
    for file_path in files_to_update:
        if file_path.is_file():
            if replace_in_file(file_path, replacements):
                modified_files.append(file_path.relative_to(REPO_ROOT))

    if modified_files:
        print_success(f"Updated {len(modified_files)} files")
        if len(modified_files) <= 20:  # Show list if reasonable
            for f in modified_files[:20]:
                print(f"  • {f}")
            if len(modified_files) > 20:
                print(f"  ... and {len(modified_files) - 20} more")

    # Rename package directory if needed
    if config["package_name"] != current.get("package_name"):
        rename_package_directory(
            current.get("package_name", DEFAULT_VALUES["package_name"]),
            config["package_name"]
        )

    print_success("\nConfiguration applied successfully!")

def show_next_steps(config: Dict[str, str]) -> None:
    """Show next steps after configuration."""
    print_header("NEXT STEPS")

    print("Your template is now customized! Here's what to do next:\n")

    print(colored("1. Review Changes", Colors.BOLD))
    print("   git status")
    print("   git diff\n")

    print(colored("2. Test Your Package", Colors.BOLD))
    print(f"   uv run {config['cli_command']} --version")
    print(f"   uv run {config['cli_command']} hello world\n")

    print(colored("3. Run Tests", Colors.BOLD))
    print("   uv run pytest\n")

    print(colored("4. Update Your Code", Colors.BOLD))
    print(f"   • Add your logic to src/{config['package_name']}/")
    print("   • Update tests in tests/")
    print("   • Customize documentation in docs/\n")

    print(colored("5. Configure Distribution (Optional)", Colors.BOLD))
    print("   • Set up platform-specific secrets in GitHub")
    print("   • Review .github/workflows/ for publishing workflows")
    print("   • Update packaging/ configs with your package details\n")

    print(colored("6. Commit Changes", Colors.BOLD))
    print("   git add .")
    print(f"   git commit -m 'chore: Initialize template for {config['project_name']}'")
    print("   git push\n")

    print_info("For more help, see:")
    print("  • docs/contributing/DEVELOPER-GUIDE.md")
    print("  • docs/distribution/PLATFORM-SUPPORT.md")

def main() -> int:
    """Main entry point."""
    print_header("PROVENANCE TEMPLATE INITIALIZATION")

    print("This wizard will help you customize the provenance-template for your project.")
    print("It's safe to run multiple times - your current config will be detected.\n")

    # Check if already customized
    customized, unchanged = is_customized()

    if customized:
        print_success("Template is already customized!")
    else:
        print_warning(f"Template uses default values for: {', '.join(unchanged)}")

    print("\nPress Enter to continue, or Ctrl+C to exit...")
    try:
        input()
    except (KeyboardInterrupt, EOFError):
        print("\n\nExiting.")
        return 0

    # Gather configuration
    config = get_project_config()

    # Confirm changes
    if not confirm_changes(config):
        print("\nNo changes made.")
        return 0

    # Apply configuration
    apply_configuration(config)

    # Show next steps
    show_next_steps(config)

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyboardInterrupt, EOFError):
        print("\n\nInterrupted. No changes made.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
