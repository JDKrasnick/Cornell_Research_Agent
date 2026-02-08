"""Interactive chat command implementation."""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from agent.agent import LabMatcherAgent
from ..output.tool_display import ToolDisplayManager


def run(args):
    """Run interactive chat mode."""
    console = Console()

    # Welcome banner
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Cornell Research Lab Matchmaker[/bold cyan]\n\n"
        "Find faculty and research opportunities at Cornell University\n\n"
        "[dim]Commands: /quit, /reset, /help, /verbose[/dim]",
        border_style="cyan"
    ))
    console.print()

    # Initialize tool display manager
    tool_display = ToolDisplayManager(console, verbose=args.verbose if not args.quiet else False)

    # Initialize agent with tool callback
    agent = LabMatcherAgent(
        tool_callback=tool_display.handle_tool_event if not args.quiet else None,
        verbose=args.verbose
    )

    # Main interaction loop
    while True:
        try:
            user_input = console.input("[bold green]You:[/bold green] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Goodbye![/yellow]")
            break

        # Handle slash commands
        if user_input.startswith('/'):
            command_result = handle_command(user_input, agent, tool_display, console, args)
            if command_result == 'quit':
                break
            continue

        if not user_input:
            continue

        # Run agent with status indicator
        console.print()
        with console.status("[bold cyan]Thinking...", spinner="dots"):
            try:
                response = agent.run(user_input)
            except Exception as e:
                console.print(f"[red]Error:[/red] {str(e)}")
                if args.verbose:
                    console.print_exception()
                continue

        # Display response
        console.print(Panel(
            Markdown(response),
            title="[bold blue]Agent",
            border_style="blue",
            padding=(1, 2)
        ))
        console.print()

    return 0


def handle_command(command: str, agent: LabMatcherAgent, tool_display: ToolDisplayManager,
                   console: Console, args) -> str:
    """
    Handle slash commands in interactive mode.

    Returns:
        'quit' if user wants to exit, 'continue' otherwise
    """
    command = command.lower().strip()

    if command == '/quit' or command == '/exit' or command == '/q':
        console.print("[yellow]Goodbye![/yellow]")
        return 'quit'

    elif command == '/reset':
        agent.reset()
        console.print("[green]✓[/green] Conversation reset\n")
        return 'continue'

    elif command == '/verbose':
        # Toggle verbosity
        tool_display.set_verbose(not tool_display.verbose)
        status = "enabled" if tool_display.verbose else "disabled"
        console.print(f"[green]✓[/green] Verbose mode {status}\n")
        return 'continue'

    elif command == '/help' or command == '/?':
        show_help(console)
        return 'continue'

    else:
        console.print(f"[yellow]Unknown command:[/yellow] {command}")
        console.print("[dim]Available commands: /quit, /reset, /help, /verbose[/dim]\n")
        return 'continue'


def show_help(console: Console):
    """Display help information."""
    help_text = """
## Available Commands

- **/quit** or **/exit** - Exit the chat
- **/reset** - Clear conversation history and start over
- **/verbose** - Toggle detailed tool execution display
- **/help** - Show this help message

## Tips

- Ask about specific research areas (e.g., "I'm interested in machine learning for healthcare")
- Request faculty matches and follow up with questions about specific professors
- Ask to draft emails to professors you're interested in
- The agent can search publications, visit lab websites, and provide detailed information
    """
    console.print(Panel(
        Markdown(help_text),
        title="[bold cyan]Help",
        border_style="cyan"
    ))
    console.print()
