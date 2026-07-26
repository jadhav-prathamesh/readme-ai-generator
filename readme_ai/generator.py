"""Communication with the Anthropic API (Claude) for README generation."""

from __future__ import annotations

import json
import os
import re
from typing import Any

import anthropic

CLAUDE_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

SYSTEM_PROMPT = """You are an expert AI technical writer and documentation engineer.
Your task is to analyze a codebase's directory structure, key metadata/manifest files, and sampled source code,
and generate a production-ready, beautiful, and highly accurate README.md for the project.

You MUST respond with ONLY valid JSON. Do NOT wrap the JSON in markdown code fences or any other formatting.
The response must be a plain JSON object with these exact keys:
- "overview": A catchy title (using "# ") followed by badges (if applicable) and a 1-2 paragraph description of the project.
- "features": A bulleted list of key features.
- "installation": Step-by-step instructions on how to install or build the project.
- "usage": Code snippets and commands showing how to use the project.
- "api": Briefly describe main API/CLI endpoints (or state "N/A" if not applicable).
- "license": A brief license statement (e.g. "Apache License 2.0" or "See LICENSE file").

IMPORTANT: Return ONLY the raw JSON object. No markdown formatting, no code fences, no backticks, no explanation text before or after.

Example output format:
{"overview": "# My Project\\n\\nDescription here.", "features": "- Feature A\\n- Feature B", "installation": "...", "usage": "...", "api": "...", "license": "..."}

Tailor the README to the specific framework and language you detect in the code.
Do not hallucinate features. If something is unknown, infer it intelligently or provide a template placeholder."""


class ReadmeGenerator:
    """Generates README content using Claude."""

    def __init__(self, api_key: str | None = None) -> None:
        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            self.client = anthropic.Anthropic()

    def generate(self, project_context: dict[str, Any]) -> str:
        """Send project context to Claude and return the generated README.md text.

        Parameters
        ----------
        project_context : dict[str, Any]
            Dictionary with keys ``project_name``, ``directory_tree``,
            ``manifests``, and ``sample_files``.

        Returns
        -------
        str
            Fully rendered README markdown.
        """
        prompt = self._build_prompt(project_context)

        try:
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=4000,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )

            json_text = self._extract_text(response)
            json_text = self._strip_markdown_fences(json_text)
            data = json.loads(json_text)
            return self._build_markdown(data)

        except anthropic.AuthenticationError:
            raise RuntimeError(
                "Anthropic API key is missing or invalid. "
                "Set ANTHROPIC_API_KEY environment variable."
            )
        except (anthropic.APIError, ValueError, KeyError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to generate README: {e!s}")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_prompt(ctx: dict[str, Any]) -> str:
        lines = [f"Project Name: {ctx.get('project_name')}\n"]
        lines.append(f"Directory Tree:\n{ctx.get('directory_tree', '')}\n")
        lines.append("Manifests:\n")
        for name, content in ctx.get("manifests", {}).items():
            lines.append(f"--- {name} ---\n{content}\n")
        lines.append("Sample Sources:\n")
        for name, content in ctx.get("sample_files", {}).items():
            lines.append(f"--- {name} ---\n{content}\n")
        return "\n".join(lines)

    @staticmethod
    def _extract_text(response: anthropic.types.Message) -> str:
        content = response.content
        if isinstance(content, str):
            return content
        for block in content:
            if isinstance(block, anthropic.types.TextBlock):
                return block.text
        raise ValueError("Claude returned an empty response.")

    @staticmethod
    def _strip_markdown_fences(text: str) -> str:
        """Remove leading/trailing markdown code fences (e.g. `` ```json ``)."""
        text = text.strip()
        text = re.sub(r"^```\w*\s*", "", text)
        text = re.sub(r"\s*```\s*$", "", text)
        return text.strip()

    @staticmethod
    def _build_markdown(data: dict[str, str]) -> str:
        """Stitch the JSON sections into a single Markdown string."""
        sections = []

        if "overview" in data:
            sections.append(data["overview"].strip())

        if "features" in data:
            sections.append(f"\n## ✨ Features\n{data['features'].strip()}")

        if "installation" in data:
            sections.append(f"\n## 🚀 Installation\n{data['installation'].strip()}")

        if "usage" in data:
            sections.append(f"\n## 📖 Usage\n{data['usage'].strip()}")

        if "api" in data and data["api"].strip().lower() not in ("n/a", "none"):
            sections.append(f"\n## 🔌 API Reference\n{data['api'].strip()}")

        if "license" in data:
            sections.append(f"\n## 📄 License\n{data['license'].strip()}")

        return "\n".join(sections)

