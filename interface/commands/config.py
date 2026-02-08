"""Configuration validation command."""

import os
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from config.settings import settings


def run(args):
    """Run configuration validation command."""
    console = Console()

    # Display current configuration
    console.print(Panel.fit(
        "[bold cyan]Cornell Lab Matcher Configuration[/bold cyan]",
        border_style="cyan"
    ))
    console.print()

    # API Keys
    api_table = Table(title="API Keys", show_header=True)
    api_table.add_column("Key", style="cyan")
    api_table.add_column("Status", style="bold")

    api_keys = {
        "ANTHROPIC_API_KEY": settings.anthropic_api_key,
        "OPENAI_API_KEY": settings.openai_api_key,
        "SEMANTIC_SCHOLAR_API_KEY": settings.semantic_scholar_api_key,
    }

    for key_name, key_value in api_keys.items():
        if key_value:
            status = "[green]✓ Set[/green]"
        else:
            status = "[yellow]✗ Not set[/yellow]"
        api_table.add_row(key_name, status)

    console.print(api_table)
    console.print()

    # Paths
    path_table = Table(title="Data Paths", show_header=True)
    path_table.add_column("Path", style="cyan")
    path_table.add_column("Location", style="dim")
    path_table.add_column("Exists", style="bold")

    paths = {
        "Database": settings.database_path,
        "Vector Store": settings.vector_store_path,
        "Raw Data": settings.raw_data_path,
        "Processed Data": settings.processed_data_path,
    }

    for path_name, path_value in paths.items():
        exists = "[green]✓[/green]" if path_value.exists() else "[yellow]✗[/yellow]"
        path_table.add_row(path_name, str(path_value), exists)

    console.print(path_table)
    console.print()

    # Model settings
    model_table = Table(title="Model Settings", show_header=True)
    model_table.add_column("Setting", style="cyan")
    model_table.add_column("Value", style="bold")

    model_table.add_row("LLM Model", settings.llm_model)
    model_table.add_row("Embedding Model", settings.embedding_model)

    console.print(model_table)
    console.print()

    # Validation check
    if args.check:
        console.print("[bold]Validation Results:[/bold]\n")

        issues = []

        # Check critical API key
        if not settings.anthropic_api_key:
            issues.append("❌ ANTHROPIC_API_KEY is required for agent functionality")

        # Check database
        if not settings.database_path.exists():
            issues.append(f"❌ Database not found at {settings.database_path}")
            issues.append("   Run: python scripts/scrape_all.py")

        # Check vector store
        if not settings.vector_store_path.exists():
            issues.append(f"❌ Vector store not found at {settings.vector_store_path}")
            issues.append("   Run: python scripts/build_embeddings.py")

        if issues:
            for issue in issues:
                console.print(f"[yellow]{issue}[/yellow]")
            console.print()
            console.print("[yellow]⚠ Configuration has issues[/yellow]")
            return 1
        else:
            console.print("[green]✓ All checks passed![/green]")
            console.print("[dim]System is ready to use[/dim]")

    return 0
