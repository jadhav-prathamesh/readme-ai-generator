"""Module for communicating with the Anthropic API (Claude) to generate the README sections."""

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
Do not hallucinate features. If something is unknown, infer it intelligently or provide a template placeholder.
"""


class ReadmeGenerator:
    """Generates README content using Claude."""

    def __init__(self, api_key: str | None = None):
        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            self.client = anthropic.Anthropic()  # Will resolve from environment automatically

    def generate(self, project_context: dict[str, Any]) -> str:
        """Sends project context to Claude and generates README.md."""

        # Build prompt payload
        prompt = f"Project Name: {project_context.get('project_name')}\n\n"
        prompt += f"Directory Tree:\n{project_context.get('directory_tree', '')}\n\n"

        prompt += "Manifests:\n"
        for name, content in project_context.get("manifests", {}).items():
            prompt += f"--- {name} ---\n{content}\n\n"

        prompt += "Sample Sources:\n"
        for name, content in project_context.get("sample_files", {}).items():
            prompt += f"--- {name} ---\n{content}\n\n"

        # Define structured output schema
        try:
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=4000,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract text output
            json_text = ""
            for block in response.content:
                if block.type == "text":
                    json_text = block.text
                    break

            if not json_text:
                raise ValueError("Claude returned an empty response.")

            # Strip markdown code fences if present (common with local proxies)
            json_text = json_text.strip()
            if json_text.startswith("```"):
                # Remove opening fence (```json / ``` )
                json_text = re.sub(r"^```\w*\s*", "", json_text)
                # Remove closing fence
                json_text = re.sub(r"\s*```\s*$", "", json_text)
                json_text = json_text.strip()

            if not json_text:
                raise ValueError("Claude returned an empty JSON payload.")

            data = json.loads(json_text)
            return self._build_markdown(data)

        except anthropic.AuthenticationError:
            raise RuntimeError("Anthropic API Key is missing or invalid. Set ANTHROPIC_API_KEY environment variable.")
        except (anthropic.APIError, ValueError, KeyError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to generate README: {e!s}")

    @staticmethod
    def _build_markdown(data: dict[str, str]) -> str:
        """Stitches the JSON sections into a single Markdown string."""
        md = []

        if "overview" in data:
            md.append(data["overview"].strip())

        if "features" in data:
            md.append("\n## ✨ Features\n" + data["features"].strip())

        if "installation" in data:
            md.append("\n## 🚀 Installation\n" + data["installation"].strip())

        if "usage" in data:
            md.append("\n## 📖 Usage\n" + data["usage"].strip())

        if "api" in data and data["api"].strip().lower() not in ["n/a", "none"]:
            md.append("\n## 🔌 API Reference\n" + data["api"].strip())

        if "license" in data:
            md.append("\n## 📄 License\n" + data["license"].strip())

        return "\n".join(md)
