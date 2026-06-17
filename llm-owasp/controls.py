"""Loads OWASP LLM Top 10 control definitions from the docs/ folder."""

from pathlib import Path

DOCS_DIR = Path(__file__).parent.parent / "docs"

CONTROL_FILES = [
    "LLM01_PromptInjection.md",
    "LLM02_SensitiveInformationDisclosure.md",
    "LLM03_SupplyChain.md",
    "LLM04_DataAndModelPoisoning.md",
    "LLM05_ImproperOutputHandling.md",
    "LLM06_ExcessiveAgency.md",
    "LLM07_SystemPromptLeakage.md",
    "LLM08_VectorAndEmbeddingWeaknesses.md",
    "LLM09_Misinformation.md",
    "LLM10_UnboundedConsumption.md",
]


def load_controls(docs_dir: Path | None = None, control_id: str | None = None) -> str:
    """Load OWASP control definitions as a single text block.

    Args:
        docs_dir: Override path to docs directory. Defaults to project docs/.
        control_id: If provided (e.g. "LLM01"), load only that control.

    Returns:
        Combined markdown text of the requested controls.
    """
    docs_dir = docs_dir or DOCS_DIR
    sections = []

    files = CONTROL_FILES
    if control_id:
        prefix = control_id.upper()
        files = [f for f in CONTROL_FILES if f.startswith(prefix)]
        if not files:
            raise ValueError(f"Unknown control ID: {control_id}. Valid IDs: LLM01–LLM10")

    for filename in files:
        filepath = docs_dir / filename
        if filepath.exists():
            content = filepath.read_text()
            sections.append(content)
        else:
            sections.append(f"# {filename} — NOT FOUND\n")

    return "\n---\n\n".join(sections)


def load_control_ids() -> list[dict]:
    """Return structured list of control IDs and names for report formatting."""
    return [
        {"id": "LLM01", "name": "Prompt Injection"},
        {"id": "LLM02", "name": "Sensitive Information Disclosure"},
        {"id": "LLM03", "name": "Supply Chain"},
        {"id": "LLM04", "name": "Data and Model Poisoning"},
        {"id": "LLM05", "name": "Improper Output Handling"},
        {"id": "LLM06", "name": "Excessive Agency"},
        {"id": "LLM07", "name": "System Prompt Leakage"},
        {"id": "LLM08", "name": "Vector and Embedding Weaknesses"},
        {"id": "LLM09", "name": "Misinformation"},
        {"id": "LLM10", "name": "Unbounded Consumption"},
    ]
