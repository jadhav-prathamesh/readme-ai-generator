"""Terminal Markdown preview using Rich."""

from __future__ import annotations

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()


def render_preview(markdown_content: str, project_name: str) -> None:
    """Render the generated Markdown in a styled terminal panel.

    Parameters
    ----------
    markdown_content : str
        The raw markdown string to preview.
    project_name : str
        Name of the project (shown in panel title).
    """
    console.print()
    panel = Panel(
        Markdown(markdown_content),
        title=f"[bold cyan]📄 Preview: README.md for {project_name}[/bold cyan]",
        expand=False,
        border_style="cyan",
    )
    console.print(panel)
    console.print()

