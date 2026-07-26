"""Module for handling terminal Markdown preview using Rich."""

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()

def render_preview(markdown_content: str, project_name: str) -> None:
    """Renders the generated Markdown beautifully in the terminal."""
    console.print("\n")

    # Create the markdown object
    md = Markdown(markdown_content)

    # Wrap in a stylish panel
    panel = Panel(
        md,
        title=f"[bold cyan]Preview: README.md for {project_name}[/bold cyan]",
        expand=False,
        border_style="cyan"
    )

    console.print(panel)
    console.print("\n")
