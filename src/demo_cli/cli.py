import argparse
import sys
import io
from . import __version__

# Fix Windows encoding for emoji/Unicode characters
if sys.platform == "win32":
    # Reconfigure stdout and stderr to use UTF-8 encoding on Windows
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Try to import rich for better formatting
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def print_welcome():
    """Print a welcome message with usage examples."""
    if RICH_AVAILABLE:
        console = Console()

        welcome_text = Text()
        welcome_text.append("🎉 Welcome to Provenance Demo!\n\n", style="bold cyan")
        welcome_text.append("A production-ready Python CLI template with enterprise-grade supply chain security.\n\n", style="dim")

        welcome_text.append("Quick Start:\n", style="bold yellow")
        welcome_text.append("  provenance-demo --version       ", style="cyan")
        welcome_text.append("  Show version\n", style="dim")
        welcome_text.append("  provenance-demo hello world     ", style="cyan")
        welcome_text.append("  Test basic functionality\n", style="dim")
        welcome_text.append("  provenance-demo verify          ", style="cyan")
        welcome_text.append("  Run 14-check security verification\n\n", style="dim")

        welcome_text.append("Documentation:\n", style="bold yellow")
        welcome_text.append("  GitHub: ", style="dim")
        welcome_text.append("https://github.com/redoubt-cysec/provenance-template\n", style="cyan underline")
        welcome_text.append("  Docs:   ", style="dim")
        welcome_text.append("docs/README.md\n\n", style="cyan")

        welcome_text.append("Use ", style="dim")
        welcome_text.append("provenance-demo --help", style="cyan")
        welcome_text.append(" for more options", style="dim")

        console.print(Panel(welcome_text, border_style="cyan", padding=(1, 2)))
    else:
        print("=" * 70)
        print("🎉 Welcome to Provenance Demo!")
        print("=" * 70)
        print()
        print("A production-ready Python CLI template with enterprise-grade supply chain security.")
        print()
        print("Quick Start:")
        print("  provenance-demo --version       Show version")
        print("  provenance-demo hello world     Test basic functionality")
        print("  provenance-demo verify          Run 14-check security verification")
        print()
        print("Documentation:")
        print("  GitHub: https://github.com/redoubt-cysec/provenance-template")
        print("  Docs:   docs/README.md")
        print()
        print("Use 'provenance-demo --help' for more options")
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        prog="provenance-demo",
        description="Demo Secure CLI — reproducible & attestable release example",
        epilog="For more information, visit: https://github.com/redoubt-cysec/provenance-template",
    )
    parser.add_argument("--version", action="store_true", help="Show version and exit")

    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Verify subcommand
    verify_parser = subparsers.add_parser(
        "verify",
        help="Verify attestations and signatures (14 comprehensive checks)"
    )
    verify_parser.add_argument(
        "--file",
        help="Path to binary to verify (default: running binary)"
    )
    verify_parser.add_argument(
        "--checks",
        help="Run specific checks only (comma-separated, e.g., checksum,signature)"
    )
    verify_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    verify_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output with timing information"
    )
    verify_parser.add_argument(
        "--output", "-o",
        help="Save verification report to file"
    )

    # Hello subcommand
    hello_parser = subparsers.add_parser(
        "hello",
        help="Say hello to NAME (test command)"
    )
    hello_parser.add_argument("name", nargs="?", default="world", help="Name to greet")

    args = parser.parse_args()

    if args.version:
        if RICH_AVAILABLE:
            console = Console()
            version_text = Text()
            version_text.append("provenance-demo ", style="bold cyan")
            version_text.append(f"v{__version__}\n", style="bold green")
            version_text.append("✅ Production-ready secure Python CLI template", style="dim")
            console.print(version_text)
        else:
            print(f"provenance-demo v{__version__}")
            print("✅ Production-ready secure Python CLI template")
        return 0

    # Handle verify subcommand
    if args.command == "verify":
        try:
            from .verify import verify_command
            return verify_command(args)
        except ImportError as e:
            print(f"❌ Error: verify module not available: {e}", file=sys.stderr)
            return 1

    # Handle hello subcommand
    if args.command == "hello":
        name = args.name or "world"
        if RICH_AVAILABLE:
            console = Console()
            console.print(f"👋 ", end="")
            console.print(f"Hello, {name}!", style="bold green")
            console.print("✅ Basic functionality working correctly", style="dim")
        else:
            print(f"👋 Hello, {name}!")
            print("✅ Basic functionality working correctly")
        return 0

    # No command provided - show welcome message
    print_welcome()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
