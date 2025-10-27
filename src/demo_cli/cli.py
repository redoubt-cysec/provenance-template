import argparse
import sys
from . import __version__

def main():
    parser = argparse.ArgumentParser(
        prog="demo",
        description="Demo Secure CLI — reproducible & attestable release example",
    )
    parser.add_argument("--version", action="store_true", help="Show version and exit")

    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Verify subcommand
    verify_parser = subparsers.add_parser(
        "verify",
        help="Verify attestations and signatures"
    )
    verify_parser.add_argument(
        "--file",
        help="Path to binary to verify (default: running binary)"
    )

    # Hello subcommand
    hello_parser = subparsers.add_parser(
        "hello",
        help="Say hello to NAME"
    )
    hello_parser.add_argument("name", nargs="?", default="world", help="Name to greet")

    args = parser.parse_args()

    if args.version:
        print(__version__)
        return 0

    # Handle verify subcommand
    if args.command == "verify":
        try:
            from .verify import verify_command
            return verify_command(args)
        except ImportError as e:
            print(f"Error: verify module not available: {e}", file=sys.stderr)
            return 1

    # Handle hello subcommand
    if args.command == "hello":
        name = args.name or "world"
        print(f"hello, {name} 👋")
        return 0

    # No command provided
    parser.print_help()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
