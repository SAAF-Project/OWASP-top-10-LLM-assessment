"""Format OWASP LLM audit assessments into a Markdown report."""
from __future__ import annotations
import json
from datetime import date
from .auditor import Assessment

VERDICT_ICON = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "N-A": "➖"}
VERDICT_RISK = {"FAIL": "High", "WARN": "Medium", "PASS": "Low", "N-A": "Informational"}


def format_report(target: str, assessments: list[Assessment]) -> str:
    lines: list[str] = []
    lines.append(f"# OWASP LLM Top 10 Audit Report")
    lines.append(f"\n**Target:** `{target}`  ")
    lines.append(f"**Date:** {date.today().isoformat()}  ")
    lines.append(f"**Standard:** OWASP Top 10 for LLM Applications (2025 edition)  \n")

    # Scorecard table
    lines.append("## Scorecard\n")
    lines.append("| Control | Name | Verdict |")
    lines.append("|---|---|:---:|")
    for a in assessments:
        icon = VERDICT_ICON.get(a.verdict, "?")
        lines.append(f"| {a.control_id} | {a.control_name} | {icon} {a.verdict} |")
    lines.append("")

    # Summary counts
    counts = {v: sum(1 for a in assessments if a.verdict == v) for v in VERDICT_ICON}
    lines.append(
        f"**Summary:** {counts['FAIL']} FAIL · {counts['WARN']} WARN · "
        f"{counts['PASS']} PASS · {counts['N-A']} N/A\n"
    )

    # Per-control detail
    lines.append("---\n")
    lines.append("## Per-Control Detail\n")
    for a in assessments:
        icon = VERDICT_ICON.get(a.verdict, "?")
        lines.append(f"### {a.control_id} — {a.control_name} {icon}\n")
        lines.append(f"**Verdict:** {a.verdict}  ")
        lines.append(f"**Risk rating:** {VERDICT_RISK.get(a.verdict, 'Informational')}\n")
        if a.findings:
            lines.append("**Findings:**")
            for f in a.findings:
                lines.append(f"- {f}")
            lines.append("")
        if a.remediation:
            lines.append("**Remediation:**")
            for r in a.remediation:
                lines.append(f"- {r}")
            lines.append("")

    # SAAF finding schema JSON blocks for non-PASS results
    findings_json: list[dict] = []
    for i, a in enumerate(assessments, start=1):
        if a.verdict in ("FAIL", "WARN"):
            findings_json.append({
                "id": f"F-{a.control_id}",
                "title": f"{a.control_id} — {a.control_name} ({a.verdict})",
                "risk_rating": VERDICT_RISK[a.verdict],
                "observation": "; ".join(a.findings) if a.findings else a.verdict,
                "recommendation": "; ".join(a.remediation) if a.remediation else "See OWASP LLM guidance.",
                "ai_assisted": True,
                "status": "Open",
            })

    if findings_json:
        lines.append("---\n")
        lines.append("## SAAF Finding Schema (machine-readable)\n")
        lines.append("```json")
        lines.append(json.dumps(findings_json, indent=2))
        lines.append("```")

    return "\n".join(lines)
