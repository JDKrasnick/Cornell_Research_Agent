"""Batch email drafting command."""

import json

from rich.console import Console

from tools.get_faculty_details import get_faculty_details
from tools.draft_email import draft_research_inquiry_email
from ..output.formatters import format_email_draft


def run(args):
    """Run batch draft email command."""
    console = Console()

    try:
        # First, get faculty details
        if not args.quiet:
            console.print(f"[cyan]Fetching faculty information...[/cyan]")

        try:
            faculty_id = int(args.faculty_id)
            faculty = get_faculty_details(faculty_id=faculty_id, include_publications=False)
        except ValueError:
            faculty = get_faculty_details(faculty_name=args.faculty_id, include_publications=False)

        if not faculty:
            console.print(f"[red]Error:[/red] Faculty member not found: {args.faculty_id}")
            return 1

        # Draft the email
        if not args.quiet:
            console.print(f"[cyan]Drafting email to {faculty['name']}...[/cyan]\n")

        email = draft_research_inquiry_email(
            faculty_name=faculty['name'],
            faculty_research_interests=faculty.get('research_interests', 'Research areas'),
            student_name=args.student_name,
            student_background=args.background,
            student_interests=args.interests
        )

        # Output based on format
        if args.json:
            # JSON output for scripting
            print(json.dumps(email, indent=2))
        else:
            # Rich formatted output
            format_email_draft(console, email)

    except Exception as e:
        if args.verbose:
            console.print_exception()
        else:
            console.print(f"[red]Error:[/red] {str(e)}")
        return 1

    return 0
