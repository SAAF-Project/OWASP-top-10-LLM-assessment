"""Collects and normalizes input material from various sources into a text bundle."""

import os
from pathlib import Path

RELEVANT_EXTENSIONS = {
    ".py", ".js", ".ts", ".json", ".yaml", ".yml", ".toml", ".md", ".txt",
    ".cfg", ".ini", ".env.example", ".sh",
}

RELEVANT_FILENAMES = {
    "CLAUDE.md", "AGENTS.md", "settings.json", "settings.local.json",
    "Dockerfile", "docker-compose.yml", "Makefile", "pyproject.toml",
    "package.json", "requirements.txt",
}

MAX_FILE_SIZE = 50_000  # characters per file
MAX_TOTAL_SIZE = 500_000  # total characters across all files


def collect(target: str) -> str:
    """Collect material from a target path or text description.

    Args:
        target: A file path, directory path, or raw text description.

    Returns:
        A normalized text bundle ready for audit.
    """
    path = Path(target)

    if path.is_file():
        return _collect_file(path)
    elif path.is_dir():
        return _collect_directory(path)
    else:
        # Treat as raw text description
        return _collect_description(target)


def _collect_file(path: Path) -> str:
    content = path.read_text(errors="replace")[:MAX_FILE_SIZE]
    return f"## Source: {path.name}\n\n```\n{content}\n```\n"


def _collect_directory(directory: Path) -> str:
    sections = []
    total_size = 0

    # Collect tree structure first
    tree = _build_tree(directory)
    sections.append(f"## Directory Structure\n\n```\n{tree}\n```\n")

    # Collect relevant files
    files = sorted(_find_relevant_files(directory))
    for filepath in files:
        if total_size >= MAX_TOTAL_SIZE:
            sections.append(f"\n*[Truncated — reached {MAX_TOTAL_SIZE} char limit]*\n")
            break

        rel = filepath.relative_to(directory)
        try:
            content = filepath.read_text(errors="replace")[:MAX_FILE_SIZE]
        except (PermissionError, OSError):
            continue

        section = f"## File: {rel}\n\n```{filepath.suffix.lstrip('.')}\n{content}\n```\n"
        total_size += len(section)
        sections.append(section)

    return "\n".join(sections)


def _collect_description(text: str) -> str:
    return f"## Agent Description (provided by user)\n\n{text}\n"


def _find_relevant_files(directory: Path) -> list[Path]:
    results = []
    for root, dirs, files in os.walk(directory):
        # Skip hidden dirs and common non-relevant dirs
        dirs[:] = [
            d for d in dirs
            if not d.startswith(".") and d not in {"node_modules", "__pycache__", "venv", ".venv", "dist", "build"}
        ]
        for filename in files:
            filepath = Path(root) / filename
            if filename in RELEVANT_FILENAMES or filepath.suffix in RELEVANT_EXTENSIONS:
                results.append(filepath)
    return results


def _build_tree(directory: Path, prefix: str = "", max_depth: int = 4, _depth: int = 0) -> str:
    if _depth >= max_depth:
        return ""

    lines = []
    try:
        entries = sorted(directory.iterdir())
    except PermissionError:
        return ""

    entries = [
        e for e in entries
        if not e.name.startswith(".") and e.name not in {"node_modules", "__pycache__", "venv", ".venv"}
    ]

    for i, entry in enumerate(entries):
        connector = "└── " if i == len(entries) - 1 else "├── "
        lines.append(f"{prefix}{connector}{entry.name}")
        if entry.is_dir():
            extension = "    " if i == len(entries) - 1 else "│   "
            subtree = _build_tree(entry, prefix + extension, max_depth, _depth + 1)
            if subtree:
                lines.append(subtree)

    return "\n".join(lines)
