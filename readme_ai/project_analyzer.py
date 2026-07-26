"""Module responsible for analyzing local project directories or cloning remote GitHub repositories."""

import os
import shutil
import subprocess  # nosec B404
import tempfile
from pathlib import Path
from typing import Any

IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    "target",
    ".mypy_cache",
    ".pytest_cache",
    ".next",
    ".nuxt",
}

IGNORE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
}

KEY_MANIFEST_FILES = {
    "pyproject.toml",
    "requirements.txt",
    "setup.py",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "Makefile",
    "Dockerfile",
    "docker-compose.yml",
}


class ProjectAnalyzer:
    """Analyzes a project directory or remote GitHub repository."""

    def __init__(self, target: str):
        self.target = target.strip()
        self.is_remote = self._is_github_url(self.target)
        self.temp_dir: str | None = None
        self.project_path: Path | None = None

    @staticmethod
    def _is_github_url(target: str) -> bool:
        return target.startswith(("http://", "https://", "git@"))

    def prepare(self) -> Path:
        """Resolves the target to a local path, cloning remote repos if necessary."""
        if self.is_remote:
            git_exe = shutil.which("git")
            if not git_exe:
                raise RuntimeError("Git executable not found in PATH.")

            if "\n" in self.target or "\r" in self.target or self.target.startswith("-"):
                raise ValueError("Invalid repository URL pattern.")

            self.temp_dir = tempfile.mkdtemp(prefix="readme_ai_")
            try:
                subprocess.run(  # nosec B603
                    [git_exe, "clone", "--depth", "1", "--", self.target, self.temp_dir],
                    check=True,
                    capture_output=True,
                )
                self.project_path = Path(self.temp_dir)
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                self.cleanup()
                raise RuntimeError(f"Failed to clone repository '{self.target}': {e}")
        else:
            path = Path(self.target).resolve()
            if not path.exists() or not path.is_dir():
                raise ValueError(f"Local directory '{path}' does not exist or is not a directory.")
            self.project_path = path
        return self.project_path

    def analyze(self) -> dict[str, Any]:
        """Scans the project to produce a context dictionary for Claude."""
        if not self.project_path or not self.project_path.exists():
            self.prepare()

        if self.project_path is None:
            raise RuntimeError("Project path could not be resolved.")
        project_path = self.project_path

        tree_lines: list[str] = []
        manifests: dict[str, str] = {}
        sample_files: dict[str, str] = {}

        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]
            rel_root = Path(root).relative_to(project_path)
            if str(rel_root) == ".":
                depth = 0
            else:
                depth = len(rel_root.parts)

            if depth > 3:  # Limit depth of directory tree scanned
                continue

            indent = "  " * depth
            folder_name = rel_root.name if str(rel_root) != "." else project_path.name
            tree_lines.append(f"{indent}{folder_name}/")

            for file in sorted(files):
                file_path = Path(root) / file
                if file_path.suffix.lower() in IGNORE_EXTENSIONS:
                    continue

                tree_lines.append(f"{indent}  {file}")

                rel_file_path = str(file_path.relative_to(project_path))

                # Extract manifest content
                if file in KEY_MANIFEST_FILES and file not in manifests:
                    manifests[rel_file_path] = self._read_file_safe(file_path, max_chars=3000)

                # Sample up to 6 important source code files for deep context
                elif (
                    len(sample_files) < 6
                    and file_path.suffix in {".py", ".ts", ".js", ".rs", ".go", ".java", ".c", ".cpp"}
                    and not file.startswith("test_")
                ):
                    content = self._read_file_safe(file_path, max_chars=2000)
                    if content.strip():
                        sample_files[rel_file_path] = content

        tree_str = "\n".join(tree_lines[:200])  # limit tree size
        return {
            "project_name": project_path.name,
            "directory_tree": tree_str,
            "manifests": manifests,
            "sample_files": sample_files,
        }

    @staticmethod
    def _read_file_safe(path: Path, max_chars: int = 2500) -> str:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(max_chars)
                return content
        except OSError:
            return ""

    def cleanup(self) -> None:
        """Removes temporary directory if remote cloning was used."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            except OSError:
                pass
