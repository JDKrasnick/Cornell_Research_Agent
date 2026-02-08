"""Tool execution visualization with Rich formatting."""

import json
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax


class ToolDisplayManager:
    """Manages display of tool execution in the CLI with Rich formatting."""

    def __init__(self, console: Console, verbose: bool = False):
        """
        Initialize the tool display manager.

        Args:
            console: Rich Console instance for output
            verbose: If True, show full tool input/output. If False, show minimal output.
        """
        self.console = console
        self.verbose = verbose
        self.tool_stack = []  # Track nested tool calls if needed

    def handle_tool_event(self, event_type: str, data: dict):
        """
        Callback for tool execution events from the agent.

        Args:
            event_type: Either 'tool_start' or 'tool_complete'
            data: Dictionary containing tool information
        """
        if event_type == 'tool_start':
            self._display_tool_start(data)
        elif event_type == 'tool_complete':
            self._display_tool_complete(data)

    def _display_tool_start(self, data: dict):
        """Display when a tool starts executing."""
        tool_name = data['name']
        tool_input = data['input']

        if self.verbose:
            # Detailed view with JSON input
            input_json = json.dumps(tool_input, indent=2)
            syntax = Syntax(input_json, "json", theme="monokai", line_numbers=False)

            self.console.print(Panel(
                syntax,
                title=f"[bold yellow]🔧 Tool: {tool_name}[/bold yellow]",
                border_style="yellow",
                subtitle="Input Parameters"
            ))
        else:
            # Compact view
            self.console.print(f"[yellow]→[/yellow] Using tool: [bold]{tool_name}[/bold]")

    def _display_tool_complete(self, data: dict):
        """Display when a tool completes execution."""
        tool_name = data['name']
        result = data['result']

        if self.verbose:
            # Show full result (with truncation for very long outputs)
            result_preview = result[:500] + "..." if len(result) > 500 else result

            self.console.print(Panel(
                result_preview,
                title=f"[bold green]✓ Result from {tool_name}[/bold green]",
                border_style="green"
            ))
        else:
            # Just show completion
            self.console.print(f"[green]✓[/green] Completed: {tool_name}")

    def set_verbose(self, verbose: bool):
        """Toggle verbosity level."""
        self.verbose = verbose
