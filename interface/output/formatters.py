"""Rich formatting helper functions for CLI output."""

from typing import List, Dict, Any, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown


def format_faculty_table(console: Console, results: List[Dict[str, Any]], show_details: bool = True):
    """
    Display faculty search results in a Rich table.

    Args:
        console: Rich Console instance
        results: List of faculty result dictionaries
        show_details: If True, show research interests column
    """
    if not results:
        console.print("[yellow]No faculty members found[/yellow]")
        return

    table = Table(title=f"Found {len(results)} Faculty Members", show_lines=show_details)

    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="bold cyan")
    table.add_column("Department", style="blue")
    table.add_column("Similarity", justify="right", style="green")

    if show_details:
        table.add_column("Research Interests", style="dim")

    for result in results:
        row = [
            str(result.get('faculty_id', 'N/A')),
            result.get('name', 'N/A'),
            result.get('department', 'N/A'),
            f"{result.get('similarity_score', 0):.1%}",
        ]

        if show_details:
            interests = result.get('research_interests', '')
            # Truncate long research interests
            if len(interests) > 80:
                interests = interests[:77] + "..."
            row.append(interests)

        table.add_row(*row)

    console.print(table)


def format_faculty_details(console: Console, details: Dict[str, Any]):
    """
    Display detailed faculty information in Rich panels.

    Args:
        console: Rich Console instance
        details: Faculty details dictionary
    """
    if not details:
        console.print("[red]Faculty member not found[/red]")
        return

    # Main information panel
    info_lines = [
        f"**Name:** {details.get('name', 'N/A')}",
        f"**Email:** {details.get('email', 'N/A')}",
        f"**Department:** {details.get('department', 'N/A')}",
    ]

    if details.get('website_url'):
        info_lines.append(f"**Website:** {details['website_url']}")

    if details.get('profile_url'):
        info_lines.append(f"**Profile:** {details['profile_url']}")

    info_text = "\n".join(info_lines)
    console.print(Panel(
        Markdown(info_text),
        title="[bold blue]Faculty Information[/bold blue]",
        border_style="blue"
    ))

    # Research interests
    if details.get('research_interests'):
        console.print(Panel(
            details['research_interests'],
            title="[bold green]Research Interests[/bold green]",
            border_style="green"
        ))

    # Publications
    if details.get('publications'):
        console.print()
        format_publications_table(console, details['publications'],
                                 total=details.get('total_publications'))


def format_publications_table(console: Console, publications: List[Dict[str, Any]],
                              total: Optional[int] = None):
    """
    Display publications in a Rich table.

    Args:
        console: Rich Console instance
        publications: List of publication dictionaries
        total: Total number of publications (if showing subset)
    """
    if not publications:
        console.print("[yellow]No publications found[/yellow]")
        return

    title = f"Recent Publications"
    if total and total > len(publications):
        title += f" (showing {len(publications)} of {total})"

    table = Table(title=title, show_lines=True)

    table.add_column("Year", style="cyan", width=6)
    table.add_column("Title", style="bold")
    table.add_column("Venue", style="dim", width=20)
    table.add_column("Citations", justify="right", style="green", width=10)

    for pub in publications:
        # Truncate long titles
        title_text = pub.get('title', 'N/A')
        if len(title_text) > 60:
            title_text = title_text[:57] + "..."

        venue = pub.get('venue', 'N/A')
        if venue and len(venue) > 20:
            venue = venue[:17] + "..."

        table.add_row(
            str(pub.get('year', 'N/A')),
            title_text,
            venue,
            str(pub.get('citation_count', 0))
        )

    console.print(table)


def format_email_draft(console: Console, email: Dict[str, Any]):
    """
    Display email draft in a copy-paste friendly format.

    Args:
        console: Rich Console instance
        email: Email dictionary with 'subject' and 'body' keys
    """
    if not email.get('success'):
        console.print(f"[red]Error generating email:[/red] {email.get('error', 'Unknown error')}")
        return

    subject = email.get('subject', 'N/A')
    body = email.get('body', 'N/A')

    # Subject line
    console.print(Panel(
        f"[bold]{subject}[/bold]",
        title="[cyan]Subject Line[/cyan]",
        border_style="cyan"
    ))

    # Email body
    console.print(Panel(
        body,
        title="[green]Email Body[/green]",
        border_style="green"
    ))

    console.print("\n[dim]Tip: Review and personalize before sending[/dim]")
