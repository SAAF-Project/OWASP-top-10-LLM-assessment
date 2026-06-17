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
