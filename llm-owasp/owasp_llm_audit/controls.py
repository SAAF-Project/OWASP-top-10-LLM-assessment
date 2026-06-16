"""Load OWASP LLM Top 10 (2025) control definitions from docs/."""
from __future__ import annotations
import os
from pathlib import Path
from dataclasses import dataclass

DOCS_DIR = Path(__file__).parent / "docs"

CONTROL_IDS = [
    "LLM01", "LLM02", "LLM03", "LLM04", "LLM05",
    "LLM06", "LLM07", "LLM08", "LLM09", "LLM10",
]


@dataclass
class Control:
    id: str
    name: str
    description: str


def load_controls() -> list[Control]:
    controls = []
    for cid in CONTROL_IDS:
        path = DOCS_DIR / f"{cid}.md"
        if not path.exists():
            raise FileNotFoundError(f"Control definition not found: {path}")
        text = path.read_text(encoding="utf-8")
        # First line is "# LLM0X — Name"
        first_line = text.splitlines()[0].lstrip("# ").strip()
        name = first_line.split("—", 1)[-1].strip() if "—" in first_line else first_line
        controls.append(Control(id=cid, name=name, description=text))
    return controls
