"""Tests for owasp_llm_audit.report"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from owasp_llm_audit.auditor import Assessment
from owasp_llm_audit.report import format_report


def _make(control_id, verdict, findings=None, remediation=None):
    return Assessment(
        control_id=control_id,
        control_name=f"Name {control_id}",
        verdict=verdict,
        findings=findings or [],
        remediation=remediation or [],
    )


ASSESSMENTS = [
    _make("LLM01", "FAIL", ["injection found"], ["sanitise inputs"]),
    _make("LLM02", "WARN", ["possible leak"], ["add redaction"]),
    _make("LLM03", "PASS"),
    _make("LLM04", "N-A"),
]


def test_report_contains_target():
    report = format_report("my_agent.py", ASSESSMENTS)
    assert "my_agent.py" in report


def test_report_scorecard_present():
    report = format_report("t", ASSESSMENTS)
    assert "## Scorecard" in report
    assert "LLM01" in report
    assert "FAIL" in report


def test_report_summary_counts():
    report = format_report("t", ASSESSMENTS)
    assert "1 FAIL" in report
    assert "1 WARN" in report
    assert "1 PASS" in report
    assert "1 N/A" in report


def test_report_finding_schema_json():
    report = format_report("t", ASSESSMENTS)
    assert "## SAAF Finding Schema" in report
    start = report.index("```json") + 7
    end = report.index("```", start)
    findings = json.loads(report[start:end].strip())
    ids = [f["id"] for f in findings]
    assert "F-LLM01" in ids
    assert "F-LLM02" in ids
    # PASS and N-A should not appear in findings
    assert "F-LLM03" not in ids
    assert "F-LLM04" not in ids


def test_report_pass_has_no_findings_section():
    report = format_report("t", [_make("LLM03", "PASS")])
    # PASS controls should not emit a Findings section
    assert "**Findings:**" not in report
