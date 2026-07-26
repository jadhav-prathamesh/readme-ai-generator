"""Tests for the ProjectAnalyzer class."""

import tempfile
from pathlib import Path

from readme_ai.project_analyzer import ProjectAnalyzer


def test_local_directory_analysis() -> None:
    """Verify scanning a local directory collects files and manifests correctly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create dummy reqs
        req_path = temp_path / "requirements.txt"
        req_path.write_text("anthropic\nrich\n", encoding="utf-8")

        # Create dummy python file
        py_path = temp_path / "app.py"
        py_path.write_text("print('hello world')", encoding="utf-8")

        analyzer = ProjectAnalyzer(temp_dir)
        context = analyzer.analyze()

        assert "requirements.txt" in context["manifests"]
        assert "app.py" in context["sample_files"]
        assert context["project_name"] == temp_path.name
