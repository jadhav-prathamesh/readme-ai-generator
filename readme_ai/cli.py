"""Main CLI entry point for the README Generator."""

import argparse
import io
import os
import sys
from pathlib import Path

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

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI README Generator using Claude Opus 5")
    parser.add_argument(
        "-t", "--target",
        type=str,
        default=None,
        help="Local directory path or GitHub repository URL to analyze."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="README.md",
        help="Output file path (default: README.md)"
    )
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Skip interactive confirmation prompts and save file automatically."
    )
    return parser.parse_args()

def main() -> None:
    """CLI entry point."""
    args = parse_args()

    try:
        console.print("[bold green]Welcome to the AI README Generator! 🤖[/bold green]")

        # 1. Ask user for project location if not passed via CLI flag
        target_input = args.target
        if not target_input:
            target_input = questionary.text(
                "Enter a local directory path or GitHub repository URL:",
                default="."
            ).ask()

        if not target_input:
            console.print("[yellow]Operation cancelled by user.[/yellow]")
            sys.exit(0)

        # 2. Analyze the project
        with console.status(f"[cyan]Analyzing '{target_input}'...[/cyan]", spinner="dots"):
            analyzer = ProjectAnalyzer(target_input)
            try:
                analyzer.prepare()
                project_context = analyzer.analyze()
            except (RuntimeError, ValueError, OSError) as e:
                console.print(f"[bold red]Analysis Error:[/bold red] {e}")
                sys.exit(1)

        console.print(f"[green]✓ Analysis complete! Found {len(project_context['manifests'])} manifests and {len(project_context['sample_files'])} sample source files.[/green]")

        # 3. Generate README using Claude
        with console.status("[cyan]Generating README.md with Claude...[/cyan]", spinner="aesthetic"):
            try:
                generator = ReadmeGenerator()
                readme_content = generator.generate(project_context)
            except (RuntimeError, ValueError, OSError) as e:
                console.print(f"[bold red]Generation Error:[/bold red] {e}")
                analyzer.cleanup()
                sys.exit(1)

        # Cleanup cloned remote repo if applicable
        analyzer.cleanup()

        # 4. Preview the generated Markdown
        render_preview(readme_content, project_context["project_name"])

        # 5. Ask to save
        save_opt = args.yes
        if not save_opt:
            save_opt = questionary.confirm(f"Do you want to save this as {args.output}?").ask()

        if save_opt:
            out_path = Path(args.output)
            if out_path.exists() and not args.yes:
                overwrite = questionary.confirm(f"{args.output} already exists. Overwrite?").ask()
                if not overwrite:
                    console.print("[yellow]File not saved.[/yellow]")
                    sys.exit(0)

            with open(out_path, "w", encoding="utf-8") as f:
                f.write(readme_content)
            console.print(f"[bold green]✓ Successfully saved to {out_path.resolve()}[/bold green]")
        else:
            console.print("[yellow]File not saved.[/yellow]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Program interrupted by user. Exiting.[/yellow]")
        sys.exit(0)

if __name__ == "__main__":
    main()
