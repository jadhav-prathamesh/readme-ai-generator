"""Integration tests for the CLI and edge cases."""

import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from readme_ai.cli import main
from readme_ai.project_analyzer import ProjectAnalyzer


def test_invalid_github_url() -> None:
    """Verify an invalid GitHub URL raises appropriate errors."""
    with pytest.raises(ValueError, match="Invalid repository URL pattern"):
        analyzer = ProjectAnalyzer("https://github.com/some/repo\n--malicious")
        analyzer.prepare()


def test_empty_local_directory() -> None:
    """Verify scanning an empty directory completes without failing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        analyzer = ProjectAnalyzer(temp_dir)
        context = analyzer.analyze()
        assert context["project_name"] == Path(temp_dir).name
        assert len(context["manifests"]) == 0
        assert len(context["sample_files"]) == 0


def test_nonexistent_local_directory() -> None:
    """Verify scanning a non-existent directory raises ValueError."""
    non_existent = "/tmp/does_not_exist_readme_ai_9999"
    analyzer = ProjectAnalyzer(non_existent)
    with pytest.raises(ValueError, match="does not exist or is not a directory"):
        analyzer.prepare()


@patch("sys.argv", ["readme-ai", "-t", "."])
@patch("readme_ai.cli.ReadmeGenerator.generate")
@patch("readme_ai.cli.render_preview")
@patch("questionary.confirm")
def test_cli_integration_success(mock_confirm: Any, mock_render: Any, mock_generate: Any) -> None:
    """Test successful CLI execution with mocked API & user interaction."""
    # Setup mocks
    mock_generate.return_value = "# Mock README\nFeatures!"
    mock_confirm.return_value.ask.return_value = False  # Skip saving file

    with (
        tempfile.TemporaryDirectory() as temp_dir,
        patch("sys.argv", ["readme-ai", "-t", temp_dir]),
    ):
        # This should complete successfully and not raise SystemExit
        try:
            main()
        except SystemExit as e:
            assert e.code == 0, f"CLI exited with error code {e.code}"

        mock_generate.assert_called_once()
        mock_render.assert_called_once()
