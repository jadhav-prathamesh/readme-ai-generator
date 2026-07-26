"""Main CLI entry point for the README Generator."""

from __future__ import annotations

import argparse
import io
import os
import sys
from pathlib import Path
from typing import NoReturn

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    stdout = sys.stdout
    if isinstance(stdout, io.TextIOWrapper):
        try:
            stdout.reconfigure(encoding="utf-8")
        except (OSError, AttributeError):
            pass

# Load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import questionary
from rich.console import Console

from readme_ai.generator import ReadmeGenerator
from readme_ai.preview import render_preview
from readme_ai.project_analyzer import ProjectAnalyzer

console = Console()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Parameters
    ----------
    argv : list[str] | None
        Argument list to parse (defaults to ``sys.argv[1:]``).

    Returns
    -------
    argparse.Namespace
        Parsed arguments.
    """
    import importlib.metadata

    try:
        ver = importlib.metadata.version("readme-ai-generator")
    except importlib.metadata.PackageNotFoundError:
        ver = "0.1.0"

    parser = argparse.ArgumentParser(
        prog="readme-ai",
        description="Generate beautiful, production-ready README.md files using Claude AI.",
        epilog="Visit https://github.com/jadhav-prathamesh/readme-ai-generator for more info.",
    )
    parser.add_argument(
        "-t", "--target",
        type=str,
        default=None,
        help="Local directory path or GitHub repository URL to analyze (default: current directory).",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="README.md",
        help="Output file path (default: README.md).",
    )
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Skip interactive confirmation prompts and save automatically.",
    )
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"readme-ai v{ver}",
        help="Show version information and exit.",
    )
    return parser.parse_args(argv)


def _exit_error(message: str, code: int = 1) -> NoReturn:
    """Print an error message and exit."""
    console.print(f"[bold red]Error:[/bold red] {message}")
    sys.exit(code)


def main() -> None:
    """CLI entry point — orchestrates analysis, generation, preview, and save."""
    args = parse_args()

    try:
        console.print(
            "[bold green]━━━ Welcome to readme-ai 🤖 ━━━[/bold green]\n"
            "[dim]AI-powered README Generator[/dim]"
        )

        # 1. Ask user for project location if not passed via CLI flag
        target_input = args.target
        if not target_input:
            target_input = questionary.text(
                "Enter a local directory path or GitHub repository URL:",
                default=".",
            ).ask()

        if not target_input:
            console.print("[yellow]Operation cancelled by user.[/yellow]")
            sys.exit(0)

        # 2. Analyze the project
        with console.status(
            f"[cyan]Analyzing '{target_input}'...[/cyan]", spinner="dots"
        ):
            analyzer = ProjectAnalyzer(target_input)
            try:
                analyzer.prepare()
                project_context = analyzer.analyze()
            except (RuntimeError, ValueError, OSError) as e:
                _exit_error(f"Analysis failed: {e}")

        console.print(
            f"[green]✓[/green] Analysis complete — "
            f"{len(project_context['manifests'])} manifest(s), "
            f"{len(project_context['sample_files'])} source file(s) scanned."
        )

        # 3. Generate README using Claude
        with console.status(
            "[cyan]Generating README.md with Claude...[/cyan]", spinner="aesthetic"
        ):
            try:
                generator = ReadmeGenerator()
                readme_content = generator.generate(project_context)
            except (RuntimeError, ValueError, OSError) as e:
                _exit_error(f"Generation failed: {e}")

        # Cleanup cloned remote repo if applicable
        analyzer.cleanup()

        # 4. Preview the generated Markdown
        render_preview(readme_content, project_context["project_name"])

        # 5. Ask to save (or auto-save with --yes)
        save_opt = args.yes
        if not save_opt:
            save_opt = questionary.confirm(
                f"Do you want to save this as [bold]{args.output}[/bold]?"
            ).ask()

        if save_opt:
            out_path = Path(args.output)
            if out_path.exists() and not args.yes:
                overwrite = questionary.confirm(
                    f"[yellow]{out_path}[/yellow] already exists. Overwrite?"
                ).ask()
                if not overwrite:
                    console.print("[yellow]File not saved.[/yellow]")
                    sys.exit(0)

            out_path.write_text(readme_content, encoding="utf-8")
            console.print(
                f"[bold green]✓[/bold green] Successfully saved to "
                f"[bold]{out_path.resolve()}[/bold]"
            )
        else:
            console.print("[yellow]File not saved.[/yellow]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user. Exiting.[/yellow]")
        sys.exit(0)


if __name__ == "__main__":
    main()

