# readme-ai-generator

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/downloads/) [![Apache License](https://img.shields.io/badge/license-Apache%202.0-green)](#license) [![PyPI](https://img.shields.io/badge/pypi-readme--ai--generator-orange)](https://pypi.org/project/readme-ai-generator/)

An intelligent README.md generator powered by Claude AI. Analyze any codebase—local or remote—and automatically generate beautiful, production-ready documentation. Simply point it at your project, and let AI handle the rest.

## ✨ Features
- **AI-Powered Generation**: Uses Claude AI to intelligently analyze code and generate contextual README content
- **Multi-Source Support**: Analyze local directories or clone and analyze GitHub repositories on the fly
- **Smart Project Detection**: Automatically detects project type, dependencies, and key files (pyproject.toml, package.json, Cargo.toml, etc.)
- **Interactive CLI**: User-friendly command-line interface with optional confirmation prompts
- **Live Preview**: View generated README in a styled terminal panel before saving
- **Batch Mode**: Use `--yes` flag to skip confirmations for automation workflows
- **Flexible Output**: Save to custom file paths (default: README.md)
- **Cross-Platform**: Full UTF-8 support on Windows, macOS, and Linux

## 🚀 Installation
### Prerequisites
- Python 3.10 or higher
- An Anthropic API key (set via `ANTHROPIC_API_KEY` environment variable)
- Git (for analyzing remote repositories)

### Installation

**Via pip:**
```bash
pip install readme-ai-generator
```

**From source:**
```bash
git clone https://github.com/jadhav-prathamesh/readme-ai-generator.git
cd readme-ai-generator
pip install -e .
```

### Setup

1. Obtain an API key from [Anthropic](https://console.anthropic.com/)
2. Set your API key:
   ```bash
   export ANTHROPIC_API_KEY="your-key-here"
   ```
   Or create a `.env` file in your project directory:
   ```
   ANTHROPIC_API_KEY=your-key-here
   ```

## 📖 Usage
### Basic Usage

**Generate README for current directory:**
```bash
readme-ai
```

**Analyze a specific local directory:**
```bash
readme-ai --target ./my-project
```

**Analyze a GitHub repository:**
```bash
readme-ai --target https://github.com/user/repo
```

**Save to a custom output file:**
```bash
readme-ai --target ./my-project --output docs/README.md
```

**Skip confirmation prompts (batch mode):**
```bash
readme-ai --target ./my-project --yes
```

### Command-Line Options

```bash
readme-ai --help
```

- `-t, --target <path|url>`: Local directory or GitHub repository URL (default: current directory)
- `-o, --output <path>`: Output file path (default: README.md)
- `-y, --yes`: Skip confirmation prompts and proceed automatically

### Running from Source

```bash
python -m readme_ai --target ./my-project
```

## 🔌 API Reference
**CLI Entry Point**: `readme-ai` command

**Main Classes**:
- `ProjectAnalyzer`: Analyzes local directories or clones remote GitHub repositories; samples code and metadata
- `ReadmeGenerator`: Communicates with Anthropic API (Claude) to generate README JSON structure
- `ReadmePreview`: Renders generated README in terminal with styled formatting

**Generated README Structure** (JSON output from Claude):
- `overview`: Project title with badges and description
- `features`: Bulleted list of key features
- `installation`: Step-by-step setup instructions
- `usage`: Code examples and usage patterns
- `api`: API/CLI endpoint documentation
- `license`: License information

## 📄 License
Apache License 2.0. See the [LICENSE](LICENSE) file for details.