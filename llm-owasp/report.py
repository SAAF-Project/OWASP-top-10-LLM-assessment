"""Formats audit results into a scored markdown report."""

from datetime import datetime, timezone


STATUS_ICONS = {
    "PASS": "PASS",
    "FAIL": "FAIL",
    "WARN": "WARN",
    "N/A": "N/A",
}


def format_report(audit_result: dict, target: str) -> str:
    """Format the structured audit result into a markdown report.

    Args:
        audit_result: Parsed JSON from the auditor.
        target: The original target path or description.

    Returns:
        Formatted markdown string.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    controls = audit_result.get("controls", [])
    summary = audit_result.get("summary", "No summary provided.")

    # Calculate stats
    stats = {"PASS": 0, "FAIL": 0, "WARN": 0, "N/A": 0}
    for c in controls:
        status = c.get("status", "N/A")
        stats[status] = stats.get(status, 0) + 1

    lines = [
        "# OWASP LLM Top 10 Audit Report",
        "",
        f"**Target:** `{target}`",
        f"**Date:** {now}",
        "",
        "## Summary",
        "",
        summary,
        "",
        "## Scorecard",
        "",
        "| Control | Name | Status |",
        "|---------|------|--------|",
    ]

    for c in controls:
        status = c.get("status", "N/A")
        icon = STATUS_ICONS.get(status, status)
        lines.append(f"| {c['id']} | {c['name']} | **{icon}** |")

    lines.extend([
        "",
        f"**Results:** {stats['PASS']} Pass, {stats['FAIL']} Fail, {stats['WARN']} Warn, {stats['N/A']} N/A",
        "",
        "---",
        "",
        "## Detailed Findings",
        "",
    ])

    for c in controls:
        status = c.get("status", "N/A")
        icon = STATUS_ICONS.get(status, status)
        lines.append(f"### {c['id']}: {c['name']} — **{icon}**")
        lines.append("")

        findings = c.get("findings", [])
        if findings:
            lines.append("**Findings:**")
            for f in findings:
                lines.append(f"- {f}")
            lines.append("")

        remediation = c.get("remediation", [])
        if remediation:
            lines.append("**Remediation:**")
            for r in remediation:
                lines.append(f"- {r}")
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)
