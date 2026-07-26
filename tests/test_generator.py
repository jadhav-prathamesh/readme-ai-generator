"""Tests for the generator module."""

from readme_ai.generator import ReadmeGenerator


def test_build_markdown() -> None:
    """Verify JSON dictionary sections are stitched into Markdown clean headings."""
    data = {
        "overview": "# Awesome Project\nThis is a cool project.",
        "features": "- Feature A\n- Feature B",
        "installation": "pip install awesome",
        "usage": "awesome --run",
        "api": "N/A",  # Should be skipped
        "license": "MIT License",
    }

    markdown = ReadmeGenerator._build_markdown(data)

    assert "# Awesome Project" in markdown
    assert "## ✨ Features" in markdown
    assert "## 🚀 Installation" in markdown
    assert "## 📖 Usage" in markdown
    assert "## 🔌 API Reference" not in markdown
    assert "## 📄 License" in markdown
