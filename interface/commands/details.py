"""Batch faculty details command."""

import json

from rich.console import Console

from tools.get_faculty_details import get_faculty_details
from ..output.formatters import format_faculty_details


def run(args):
    """Run batch details command."""
    console = Console()

    if not args.quiet:
        console.print(f"[cyan]Fetching details for:[/cyan] {args.faculty_id}\n")

    try:
        # Determine if faculty_id is numeric or name
        try:
            faculty_id = int(args.faculty_id)
            details = get_faculty_details(
                faculty_id=faculty_id,
                include_publications=not args.no_publications,
                max_publications=10
            )
        except ValueError:
            # It's a name, not an ID
            details = get_faculty_details(
                faculty_name=args.faculty_id,
                include_publications=not args.no_publications,
                max_publications=10
            )

        if not details:
            console.print(f"[yellow]Faculty member not found:[/yellow] {args.faculty_id}")
            return 1

        # Output based on format
        if args.json:
            # JSON output for scripting
            print(json.dumps(details, indent=2))
        else:
            # Rich formatted output
            format_faculty_details(console, details)

    except Exception as e:
        if args.verbose:
            console.print_exception()
        else:
            console.print(f"[red]Error:[/red] {str(e)}")
        return 1

    return 0
