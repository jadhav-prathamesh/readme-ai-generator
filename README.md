# readme-ai 🤖

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](#)
[![GitHub Stars](https://img.shields.io/github/stars/jadhav-prathamesh/readme-ai-generator?style=social)](https://github.com/jadhav-prathamesh/readme-ai-generator)

**Intelligent README.md generation powered by Anthropic Claude AI.**

Analyse any local project directory or public GitHub repository and produce a production-ready, beautifully formatted `README.md` — complete with badges, feature highlights, installation guides, usage examples, API references, and license information.

---

## ✨ Features

- **🔍 Smart Project Analysis** — Scans directory trees, parses manifest files (`pyproject.toml`, `package.json`, `Cargo.toml`, etc.), and samples up to six key source files for deep context.
- **🧠 Claude-Powered Generation** — Leverages Anthropic's Claude to write clear, accurate, and well-structured documentation tailored to your project's language and framework.
- **🖥️ Rich Terminal Preview** — Preview the generated README in style using `rich` panels before saving.
- **🌐 Local & Remote Support** — Analyse a local folder or clone any public GitHub repository with `--depth 1` for speed.
- **🚀 CLI-First Design** — Full command-line interface with `-t/--target`, `-o/--output`, `-y/--yes`, file-overwrite protection, and an interactive fallback mode.

---

## 🚀 Installation

### Prerequisites

- Python 3.10 or later
- An [Anthropic API key](https://console.anthropic.com/) (set via `ANTHROPIC_API_KEY` environment variable)

### Install via pip

```bash
pip install readme-ai-generator
```

### Install from source

```bash
git clone https://github.com/jadhav-prathamesh/readme-ai-generator.git
cd readme-ai-generator
pip install -e .
```

---

## 📖 Usage

```bash
# Quick start — analyse current directory
export ANTHROPIC_API_KEY="your-key-here"
readme-ai -t . -y

# Analyse a remote GitHub repository
readme-ai -t https://github.com/user/repo -o README.md

# Interactive mode (prompts for target)
readme-ai
```

### CLI Options

| Flag | Description |
|------|-------------|
| `-t, --target` | Local path or GitHub URL to analyse (default: current dir) |
| `-o, --output` | Output file path (default: `README.md`) |
| `-y, --yes` | Skip confirmation prompts and auto-save |
| `-V, --version` | Show version and exit |
| `-h, --help` | Show help message |

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | ✅ | Your Anthropic API key |
| `ANTHROPIC_BASE_URL` | ❌ | Custom API base URL (e.g. for proxies) |
| `ANTHROPIC_MODEL` | ❌ | Claude model name (default: `claude-sonnet-4-20250514`) |
| `ANTHROPIC_AUTH_TOKEN` | ❌ | Auth token (alternative to API key) |

You may also place these in a `.env` file in the working directory.

---

## 🔌 API Reference

### `readme_ai.cli.main()`

CLI entry point. Handles argument parsing, project analysis, README generation, preview, and file saving.

### `readme_ai.generator.ReadmeGenerator`

```python
generator = ReadmeGenerator(api_key="optional-key")
markdown = generator.generate(project_context)
```

- `generate(context: dict) -> str` — Accepts a project context dictionary with keys `project_name`, `directory_tree`, `manifests`, and `sample_files`. Returns the full README markdown string.

### `readme_ai.project_analyzer.ProjectAnalyzer`

```python
analyzer = ProjectAnalyzer(target="path-or-url")
path = analyzer.prepare()          # clone remote or resolve local
context = analyzer.analyze()       # scan and build context
analyzer.cleanup()                 # remove temp clone
```

- `prepare() -> Path` — Resolves `target` to a local `Path`, cloning remote repos into a temporary directory.
- `analyze() -> dict` — Walks the project tree, collecting manifests and sample source files.
- `cleanup()` — Removes the temporary clone (no-op for local targets).

### `readme_ai.preview.render_preview()`

```python
render_preview(markdown_content, project_name)
```

Renders the markdown inside a styled `rich` panel for terminal preview.

---

## 📁 Project Structure

```
readme-ai-generator/
├── readme_ai/
│   ├── __init__.py            # Package metadata
│   ├── __main__.py            # python -m readme_ai entry point
│   ├── cli.py                 # CLI argument parsing & orchestration
│   ├── generator.py           # Claude API interaction
│   ├── preview.py             # Terminal markdown preview
│   └── project_analyzer.py    # Filesystem & git analysis
├── tests/
│   ├── test_analyzer.py
│   ├── test_cli.py
│   └── test_generator.py
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

---

## 🧪 Development

```bash
# Clone and install in editable mode
git clone https://github.com/jadhav-prathamesh/readme-ai-generator.git
cd readme-ai-generator
pip install -e .

# Run tests
pytest tests/ -v

# Generate a README
readme-ai -t . -y
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feat/my-feature`)
5. Open a Pull Request

Make sure tests pass before submitting.

---

## 📄 License

Distributed under the **Apache License 2.0**. See [`LICENSE`](LICENSE) for more information.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/jadhav-prathamesh">Prathmesh Jadhav</a>
</p>

