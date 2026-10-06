"""Tests for owasp_llm_audit.auditor (no real API calls)."""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from owasp_llm_audit.auditor import Assessment, _call, assess_all
from owasp_llm_audit.controls import Control

CTRL = Control(id="LLM01", name="Prompt Injection", description="Test control")
MATERIAL = "def foo(): pass"


def _mock_client(verdict="PASS", findings=None, remediation=None):
    import json
    payload = json.dumps({
        "verdict": verdict,
        "findings": findings or [],
        "remediation": remediation or [],
    })
    msg = MagicMock()
    msg.content = [MagicMock(text=payload)]
    client = MagicMock()
    client.messages.create.return_value = msg
    return client


def test_call_returns_assessment():
    client = _mock_client("PASS")
    result = _call(client, MATERIAL, CTRL)
    assert isinstance(result, Assessment)
    assert result.verdict == "PASS"
    assert result.control_id == "LLM01"


def test_call_fail_verdict():
    client = _mock_client("FAIL", findings=["issue found"], remediation=["fix it"])
    result = _call(client, MATERIAL, CTRL)
    assert result.verdict == "FAIL"
    assert result.findings == ["issue found"]
    assert result.remediation == ["fix it"]


def test_call_handles_markdown_fenced_json():
    import json
    from unittest.mock import MagicMock
    payload = '```json\n{"verdict": "WARN", "findings": [], "remediation": []}\n```'
    msg = MagicMock()
    msg.content = [MagicMock(text=payload)]
    client = MagicMock()
    client.messages.create.return_value = msg
    result = _call(client, MATERIAL, CTRL)
    assert result.verdict == "WARN"


def test_call_handles_truncated_json():
    msg = MagicMock()
    msg.content = [MagicMock(text='{"verdict": "FAIL", "findings": ["truncated')]
    client = MagicMock()
    client.messages.create.return_value = msg
    result = _call(client, MATERIAL, CTRL)
    assert result.verdict == "WARN"
    assert "truncated" in result.findings[0].lower()


def test_call_retries_on_rate_limit():
    import anthropic
    client = MagicMock()
    good_msg = MagicMock()
    good_msg.content = [MagicMock(text='{"verdict": "PASS", "findings": [], "remediation": []}')]
    rate_err = anthropic.RateLimitError.__new__(anthropic.RateLimitError)
    rate_err.response = MagicMock()
    rate_err.response.headers = {"retry-after": "1"}
    client.messages.create.side_effect = [rate_err, good_msg]
    result = _call(client, MATERIAL, CTRL)
    assert result.verdict == "PASS"
    assert client.messages.create.call_count == 2


def test_assess_all_returns_in_control_order():
    controls = [
        Control(id="LLM01", name="Prompt Injection", description="c1"),
        Control(id="LLM02", name="Sensitive Info", description="c2"),
    ]
    client = _mock_client("PASS")
    results = assess_all(MATERIAL, controls, client, max_workers=2)
    assert [r.control_id for r in results] == ["LLM01", "LLM02"]


def test_assess_all_calls_on_result():
    controls = [Control(id="LLM01", name="Prompt Injection", description="c")]
    client = _mock_client("PASS")
    received = []
    assess_all(MATERIAL, controls, client, on_result=received.append, max_workers=1)
    assert len(received) == 1
    assert received[0].control_id == "LLM01"


# --- never-N-A enforcement ---------------------------------------------------

@pytest.mark.parametrize("cid", ["LLM03", "LLM09", "LLM10"])
def test_never_na_controls_are_overridden_to_warn(cid):
    ctrl = Control(id=cid, name="x", description="d")
    result = _call(_mock_client("N-A"), MATERIAL, ctrl)
    assert result.verdict == "WARN"
    assert any("can never be N-A" in f for f in result.findings)


def test_other_controls_may_still_be_na():
    ctrl = Control(id="LLM08", name="Vector", description="d")
    assert _call(_mock_client("N-A"), MATERIAL, ctrl).verdict == "N-A"


def test_system_prompt_states_never_na_and_stub_rule():
    from owasp_llm_audit.auditor import SYSTEM_PROMPT
    assert "NEVER N-A" in SYSTEM_PROMPT
    assert "stub" in SYSTEM_PROMPT


# --- citation verification ---------------------------------------------------

SRC = {"agent.py": "import os\nAPI_KEY = 'abc'\nprint('hi')\n"}


def test_verify_findings_accepts_correct_citation():
    from owasp_llm_audit.auditor import verify_findings
    out, checked = verify_findings(["agent.py:2 hardcoded `API_KEY = 'abc'`"], SRC)
    assert checked == 1
    assert "citation unverified" not in out[0]


def test_verify_findings_flags_wrong_line():
    from owasp_llm_audit.auditor import verify_findings
    out, _ = verify_findings(["agent.py:3 hardcoded `API_KEY = 'abc'`"], SRC)
    assert "citation unverified" in out[0]


def test_verify_findings_does_not_flag_identifiers_or_paraphrases():
    from owasp_llm_audit.auditor import verify_findings
    findings = [
        "agent.py:3 calls `print()` and mentions `os` and `no max_tokens set`",  # identifiers / not in file
        "agent.py:3 hardcoded `API_KEY = 'abc'`-like pattern at line 2",          # in file, wrong line
    ]
    out, _ = verify_findings(findings, SRC)
    assert "citation unverified" not in out[0]
    assert "citation unverified" in out[1]


def test_verify_findings_flags_out_of_range():
    from owasp_llm_audit.auditor import verify_findings
    out, _ = verify_findings(["agent.py:99 something"], SRC)
    assert "outside the file" in out[0]


def test_verify_findings_ignores_unsubmitted_files():
    from owasp_llm_audit.auditor import verify_findings
    out, checked = verify_findings(["os.path:3 is fine"], SRC)
    assert checked == 0
    assert out == ["os.path:3 is fine"]


def test_call_flattens_non_string_findings():
    client = _mock_client("FAIL", findings=[{"location": "agent.py:2", "observation": "hardcoded key"}])
    result = _call(client, MATERIAL, CTRL, SRC)
    assert result.findings == ["location: agent.py:2; observation: hardcoded key"]


def test_call_marks_unverified_citations_when_sources_given():
    client = _mock_client("FAIL", findings=["agent.py:3 hardcoded `API_KEY = 'abc'`"])
    result = _call(client, MATERIAL, CTRL, SRC)
    assert "citation unverified" in result.findings[0]
