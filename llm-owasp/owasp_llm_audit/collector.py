"""Collect and normalise audit material from one or more paths (files or directories)."""
from __future__ import annotations
import fnmatch
import os
from pathlib import Path

SUPPORTED = {".py", ".js", ".ts", ".json", ".yaml", ".yml", ".txt", ".md"}
FILE_LIMIT = 50 * 1024       # 50 KB per file
TOTAL_LIMIT = 500 * 1024     # 500 KB total


def _gather(path: Path, filter_glob: str | None) -> list[Path]:
    """Recursively gather supported files under path, optionally filtered by glob."""
    files: list[Path] = []
    if path.is_file():
        if path.suffix.lower() in SUPPORTED:
            files.append(path)
    else:
        for root, _, names in os.walk(path):
            for name in names:
                fp = Path(root) / name
                if fp.suffix.lower() not in SUPPORTED:
                    continue
                if filter_glob and not fnmatch.fnmatch(fp.name, filter_glob):
                    continue
                files.append(fp)
    return files


def collect(targets: str | list[str], filter_glob: str | None = None) -> str:
    """Return normalised audit material from one or more paths.

    targets: a single path string or a list of path strings (files or directories).
    filter_glob: optional filename glob (e.g. 'frank-van-dissel-uc*.md') applied
                 when walking directories — avoids the need to copy files to a temp folder.
    """
    if isinstance(targets, str):
        targets = [targets]

    files: list[Path] = []
    for t in targets:
        path = Path(t)
        if not path.exists():
            raise FileNotFoundError(f"Target not found: {t}")
        files.extend(_gather(path, filter_glob))

    if not files:
        raise ValueError(f"No supported files found in: {targets} (filter={filter_glob!r})")

    parts: list[str] = []
    skipped: list[str] = []
    total = 0
    for fp in sorted(set(files)):
        raw = fp.read_bytes()[:FILE_LIMIT]
        snippet = raw.decode("utf-8", errors="replace")
        chunk = f"### {fp.name}\n```\n{snippet}\n```\n"
        if total + len(chunk) > TOTAL_LIMIT:
            # Fix 6: skip oversized file and continue with remaining files
            skipped.append(fp.name)
            continue
        parts.append(chunk)
        total += len(chunk)

    if skipped:
        parts.append(f"### [skipped — total limit reached: {', '.join(skipped)}]\n")

    return "\n".join(parts)
