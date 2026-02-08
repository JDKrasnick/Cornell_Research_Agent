"""Main CLI application for Cornell Lab Matcher."""

import argparse
import sys

from rich.console import Console

from config.settings import settings
from .commands import chat, search, details, draft, config as config_cmd


console = Console()


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="cornell-lab-matcher",
        description="Cornell Research Lab Matchmaker - Find faculty and research opportunities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s chat                     Start interactive chat
  %(prog)s search "machine learning"  Search for faculty
  %(prog)s details 123               Get faculty details
  %(prog)s draft 123 --student-name "Jane" --background "CS senior" --interests "ML research"
        """
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed tool execution information"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Minimize output (no tool visibility)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format (batch commands only)"
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Chat command (interactive mode)
    chat_parser = subparsers.add_parser(
        "chat",
        help="Interactive chat mode with the research agent"
    )

    # Search command
    search_parser = subparsers.add_parser(
        "search",
        help="Search for faculty by research interests"
    )
    search_parser.add_argument(
        "query",
        help="Research interests to search for (e.g., 'machine learning for healthcare')"
    )
    search_parser.add_argument(
        "--top-k", "-k",
        type=int,
        default=5,
        help="Number of results to return (default: 5)"
    )
    search_parser.add_argument(
        "--department", "-d",
        help="Filter by department (e.g., CS, ECE, INFO)"
    )

    # Details command
    details_parser = subparsers.add_parser(
        "details",
        help="Get detailed information about a faculty member"
    )
    details_parser.add_argument(
        "faculty_id",
        help="Faculty ID or name"
    )
    details_parser.add_argument(
        "--no-publications",
        action="store_true",
        help="Exclude publications from output"
    )

    # Draft command
    draft_parser = subparsers.add_parser(
        "draft",
        help="Draft a research inquiry email"
    )
    draft_parser.add_argument(
        "faculty_id",
        help="Faculty ID or name to email"
    )
    draft_parser.add_argument(
        "--student-name",
        required=True,
        help="Student's name"
    )
    draft_parser.add_argument(
        "--background",
        required=True,
        help="Student's background and skills"
    )
    draft_parser.add_argument(
        "--interests",
        required=True,
        help="Why interested in this professor's work"
    )

    # Config command
    config_parser = subparsers.add_parser(
        "config",
        help="Show and validate configuration"
    )
    config_parser.add_argument(
        "--check",
        action="store_true",
        help="Check if all required components are available"
    )

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Default to chat if no command specified
    if args.command is None:
        args.command = "chat"
        # Set default values for chat command
        args.verbose = getattr(args, 'verbose', False)
        args.quiet = getattr(args, 'quiet', False)

    # Validate API key (except for config command)
    if not settings.anthropic_api_key and args.command != "config":
        console.print("[red]Error: ANTHROPIC_API_KEY not found in environment[/red]")
        console.print("\n[dim]Please set it in your .env file or environment variables:")
        console.print("  export ANTHROPIC_API_KEY='your-api-key-here'[/dim]")
        return 1

    # Check for conflicting flags
    if args.quiet and args.verbose:
        console.print("[yellow]Warning: --quiet and --verbose are mutually exclusive[/yellow]")
        console.print("[dim]Using --verbose (takes precedence)[/dim]\n")
        args.quiet = False

    # Route to appropriate command
    try:
        if args.command == "chat":
            return chat.run(args)
        elif args.command == "search":
            return search.run(args)
        elif args.command == "details":
            return details.run(args)
        elif args.command == "draft":
            return draft.run(args)
        elif args.command == "config":
            return config_cmd.run(args)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        return 130
    except Exception as e:
        if getattr(args, 'verbose', False):
            console.print_exception()
        else:
            console.print(f"[red]Error:[/red] {str(e)}")
            console.print("[dim]Use --verbose for detailed error information[/dim]")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
