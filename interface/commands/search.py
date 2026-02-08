"""Batch faculty search command."""

import json

from rich.console import Console

from tools.search_faculty import search_faculty
from ..output.formatters import format_faculty_table


def run(args):
    """Run batch search command."""
    console = Console()

    if not args.quiet:
        console.print(f"[cyan]Searching for:[/cyan] {args.query}\n")

    try:
        # Direct tool call (no agent loop)
        results = search_faculty(
            query=args.query,
            n_results=args.top_k,
            min_similarity=0.0
        )

        # Output based on format
        if args.json:
            # JSON output for scripting
            print(json.dumps(results, indent=2))
        else:
            # Rich formatted table
            format_faculty_table(console, results, show_details=not args.quiet)

            if not args.quiet and results:
                console.print(f"\n[dim]Use 'cornell-lab-matcher details <ID>' for more information[/dim]")

    except Exception as e:
        if args.verbose:
            console.print_exception()
        else:
            console.print(f"[red]Error:[/red] {str(e)}")
        return 1

    return 0
