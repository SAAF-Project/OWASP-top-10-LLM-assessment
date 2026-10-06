"""
OWASP LLM Top 10 Agent Compliance Reviewer
Analyse agent source code or configs for OWASP Top 10 LLM security risks.

Usage:
  python review_agent.py                          <- paste code
  python review_agent.py my_agent.py             <- review one file
  python review_agent.py --folder agents_folder  <- review all agent files in a folder
"""

import anthropic
import os
import re
import sys
from pathlib import Path

SUPPORTED_EXTENSIONS = (".py", ".js", ".ts", ".json", ".yaml", ".yml", ".txt", ".md")

SYSTEM_PROMPT = """You are a senior application security engineer specialising in LLM security.
You review agent code, prompts, and configurations for compliance against the
OWASP Top 10 for Large Language Model Applications (2025 edition).

Controls that are never N/A:
- LLM03 Supply Chain: NEVER N/A. Having no imports or no requirements file is not evidence of
  safety: absent dependency pinning, a lockfile, or model/provider version pinning is itself a gap
  (WARN, or FAIL if dependencies exist unpinned).
- LLM09 Misinformation: NEVER N/A in an audit context.
- LLM10 Unbounded Consumption: NEVER N/A. Treat a stub, mock, or placeholder LLM call as a real
  call site: if it has no max_tokens and no input length cap, the verdict is FAIL. Do not
  downgrade to WARN because the call is a stub.

Source files are supplied with each line prefixed by its 1-based line number as `N| `. Cite those
numbers exactly (file:line). Never include the `N| ` prefix inside quoted code, and never estimate
or guess a line number.

The ten categories you must assess are:
  LLM01 – Prompt Injection
  LLM02 – Sensitive Information Disclosure
  LLM03 – Supply Chain
  LLM04 – Data and Model Poisoning
  LLM05 – Improper Output Handling
  LLM06 – Excessive Agency
  LLM07 – System Prompt Leakage
  LLM08 – Vector and Embedding Weaknesses
  LLM09 – Misinformation
  LLM10 – Unbounded Consumption

For each category that is relevant to the submitted code, output:

**LLMxx – <Category Name>**
- Status: PASS | FAIL | WARN | N/A
- Evidence: quote the exact line(s) that determined this status in a fenced code block with file:line references; write "none visible" if status is N/A
- Findings: specific lines, patterns, or design decisions that are problematic (or why it passes)
- Recommendation: concrete remediation step (skip if status is PASS or N/A)

Do not write a review date.

Then close with:

**Overall Compliance Summary**
- A table with one row for EACH of the ten controls (LLM01–LLM10), including N/A ones
- Overall risk rating: Critical | High | Medium | Low
- Top three priority fixes (numbered)
- Positive security controls already in place

Be specific. Reference actual code patterns, variable names, or config keys you observe.
Do not guess about functionality that is not visible in the submitted code."""


def read_file(file_path: str) -> str:
    """Read a source file as plain text."""
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def number_lines(code_text: str) -> str:
    """Prefix each line with its 1-based number (`N| `) so the model cites real lines."""
    return "\n".join(f"{i}| {line}" for i, line in enumerate(code_text.splitlines(), 1))


# Two citation styles are accepted inside fenced evidence blocks:
#   "# file.py:12-14" on its own line, followed by quoted code
#   "file.py:12 — quoted code" (separator: em dash, en dash, hyphen or colon)
_CITE_HEAD_RE = re.compile(r"^\s*(?:#|//)\s*(\S+?):(\d+)(?:-(\d+))?\s*$")
_CITE_INLINE_RE = re.compile(r"^\s*(\S+?\.\w+):(\d+)(?:-(\d+))?\s*[—–:-]\s*(.+?)\s*$")


def verify_citations(review_text: str, sources: dict) -> tuple:
    """Check file:line citations in fenced evidence blocks against the real sources.

    sources: {filename: code_text}. Returns (problems, checked) where problems is a list of
    human-readable strings and checked is the number of citations that could be compared.
    """
    lines_by_name = {Path(n).name: c.splitlines() for n, c in sources.items()}
    problems = []
    checked = 0
    in_block, cite = False, None

    def locate(name_raw: str, a: str, b):
        name = Path(name_raw).name
        start, end = int(a), int(b or a)
        src = lines_by_name.get(name)
        if src is None:
            problems.append(f"{name_raw}: cited file was not submitted")
            return None
        if start < 1 or end > len(src) or start > end:
            problems.append(f"{name}:{start}-{end}: outside file ({len(src)} lines)")
            return None
        return name, start, end, src[start - 1:end]

    def compare(c, quoted: str) -> None:
        nonlocal checked
        # tolerate trailing "# comment" or "..." elisions in the model's quote
        segments = [s.strip() for s in quoted.split("  #")[0].split("...") if s.strip()]
        if not segments:
            return
        checked += 1
        cited = "\n".join(c[3])
        missing = [s for s in segments if s not in cited]
        if missing:
            problems.append(f"{c[0]}:{c[1]}-{c[2]}: quoted text not found: {missing[0][:60]}")

    for raw in review_text.splitlines():
        if raw.strip().startswith("```"):
            in_block, cite = not in_block, None
            continue
        if not in_block:
            continue
        m = _CITE_HEAD_RE.match(raw)
        if m:
            cite = locate(m.group(1), m.group(2), m.group(3))
            continue
        m = _CITE_INLINE_RE.match(raw)
        if m:
            c = locate(m.group(1), m.group(2), m.group(3))
            if c:
                compare(c, m.group(4))
            continue
        quoted = raw.strip()
        if cite and quoted and not quoted.startswith(("#", "//")):
            compare(cite, quoted)
    return problems, checked


def citation_note(review_text: str, sources: dict) -> str:
    """Markdown note summarising verify_citations(); shared by the CLI and the web portal."""
    problems, checked = verify_citations(review_text, sources)
    if problems:
        return ("\n\n**Citation check:** the following cited locations did not match the "
                "submitted source and must be verified by a human:\n"
                + "\n".join(f"- {p}" for p in problems))
    if checked == 0:
        return ("\n\n**Citation check:** no file:line citations could be machine-verified; "
                "a human must verify all cited locations.")
    return f"\n\n**Citation check:** {checked} cited locations matched the submitted source."


def review_agent(code_text: str, filename: str = "<stdin>") -> str:
    """Send agent code to Claude for OWASP LLM Top 10 analysis."""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    print(f"\n--- Analysing {filename} against OWASP LLM Top 10... ---\n")

    result = []
    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Please review the following agent code/config for OWASP LLM Top 10 compliance.\n"
                    f"Filename: {filename}\n\n"
                    f"```\n{number_lines(code_text)}\n```"
                ),
            }
        ],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            result.append(text)

    review = "".join(result)
    note = citation_note(review, {filename: code_text})
    print(note, flush=True)
    print("\n--- Review complete ---\n")
    return review + note


def assess_risk(filename: str, review_text: str) -> dict:
    """Ask Claude to extract the overall risk rating from a completed review."""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=256,
        system="""You are an LLM security risk classifier.
Given an OWASP LLM Top 10 review, extract the overall risk rating and one concise reason.
Respond in exactly this format:
RISK: Critical | High | Medium | Low
REASON: one sentence""",
        messages=[
            {
                "role": "user",
                "content": f"File: {filename}\n\nReview:\n{review_text}",
            }
        ],
    )

    output = response.content[0].text.strip()
    risk_level = "Unknown"
    reason = ""

    for line in output.splitlines():
        if line.startswith("RISK:"):
            risk_level = line.replace("RISK:", "").strip()
        elif line.startswith("REASON:"):
            reason = line.replace("REASON:", "").strip()

    return {"file": filename, "risk": risk_level, "reason": reason}


def save_priority_report(assessments: list, reports_folder: str) -> None:
    """Save agents sorted by risk level (Critical first)."""
    order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Unknown": 4}
    sorted_assessments = sorted(assessments, key=lambda x: order.get(x["risk"], 4))

    report_path = os.path.join(reports_folder, "owasp_priority_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("OWASP LLM TOP 10 — AGENT PRIORITY REPORT\n")
        f.write("=" * 50 + "\n\n")
        for item in sorted_assessments:
            f.write(f"[{item['risk'].upper()}] {item['file']}\n")
            f.write(f"  → {item['reason']}\n\n")

    print("\n--- Priority Report ---\n")
    for item in sorted_assessments:
        print(f"  [{item['risk'].upper()}] {item['file']}")
        print(f"         {item['reason']}")
    print(f"\nSaved to: {report_path}")


def review_folder(folder_path: str) -> None:
    """Review all agent files in a folder, then generate a priority report."""
    if not os.path.isdir(folder_path):
        print(f"Error: Folder '{folder_path}' not found.")
        sys.exit(1)

    agent_files = [
        f for f in os.listdir(folder_path)
        if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS
    ]

    if not agent_files:
        print(f"No supported agent files found in '{folder_path}'.")
        sys.exit(1)

    reports_folder = os.path.join(folder_path, "reports")
    os.makedirs(reports_folder, exist_ok=True)

    print(f"Found {len(agent_files)} file(s) to review.")
    print(f"Reports will be saved to: {reports_folder}\n")

    assessments = []

    for i, filename in enumerate(agent_files, 1):
        file_path = os.path.join(folder_path, filename)
        print(f"[{i}/{len(agent_files)}] {filename}")

        code_text = read_file(file_path)
        review_result = review_agent(code_text, filename)

        base_name = os.path.splitext(filename)[0]
        report_path = os.path.join(reports_folder, base_name + "_owasp_review.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"OWASP LLM Top 10 Review: {filename}\n")
            f.write("=" * 50 + "\n\n")
            f.write(review_result)

        print(f"    Saved: {base_name}_owasp_review.txt")
        print(f"    Assessing risk level...")

        assessment = assess_risk(filename, review_result)
        assessments.append(assessment)
        print(f"    Risk: {assessment['risk']}\n")

    print(f"\nAll {len(agent_files)} file(s) reviewed. Generating priority report...")
    save_priority_report(assessments, reports_folder)


def main():
    # Option 1: folder mode
    if len(sys.argv) > 2 and sys.argv[1] == "--folder":
        review_folder(sys.argv[2])

    # Option 2: single file
    elif len(sys.argv) > 1:
        file_path = sys.argv[1]
        try:
            print(f"Reviewing file: {file_path}")
            code_text = read_file(file_path)
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            sys.exit(1)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
        review_agent(code_text, os.path.basename(file_path))

    # Option 3: paste mode
    else:
        print("Paste your agent code below.")
        print("When done, press Enter, then Ctrl+Z (Windows) and Enter to submit.\n")
        lines = []
        try:
            for line in sys.stdin:
                lines.append(line)
        except KeyboardInterrupt:
            pass
        code_text = "".join(lines).strip()
        if not code_text:
            print("No code provided. Exiting.")
            sys.exit(1)
        review_agent(code_text)


if __name__ == "__main__":
    main()
