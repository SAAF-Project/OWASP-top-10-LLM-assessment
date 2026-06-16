"""Assess audit material against OWASP LLM controls via Claude API."""
from __future__ import annotations
import json
import random
import time
import anthropic
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

# Fix 1: import using package-relative path so the module works from any cwd
from .controls import Control

MODEL = "claude-opus-4-6"

SYSTEM_PROMPT = """\
You are an AI security auditor specialised in the OWASP Top 10 for LLM Applications (2025 edition).
Given audit material (agent plan, codebase, configuration, or architecture description) and a single
OWASP LLM control definition, assess whether the target passes, fails, warns, or is not applicable
for this control.

Return ONLY a valid JSON object with these fields:
- verdict: one of PASS, FAIL, WARN, N-A
- findings: list of strings (evidence from the material; empty list for PASS/N-A)
- remediation: list of actionable recommendation strings (empty list for PASS/N-A)

Base your assessment ONLY on evidence present in the provided material. Do not invent findings.
"""


@dataclass
class Assessment:
    control_id: str
    control_name: str
    verdict: str          # PASS | FAIL | WARN | N-A
    findings: list[str]
    remediation: list[str]


# Fix 2: client created once and passed in; assess() is pure
def _call(client: anthropic.Anthropic, material: str, control: Control) -> Assessment:
    user_message = f"""\
Control: {control.id} - {control.name}

Control definition:
{control.description}

---

Audit material:
{material}

---

Assess this agent against the control above. Return JSON only.
"""
    response = None
    for attempt in range(3):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            )
            break
        except anthropic.RateLimitError as exc:
            if attempt == 2:
                raise
            try:
                wait = int(exc.response.headers.get("retry-after", 0))
            except Exception:
                wait = 0
            if not wait:
                wait = (2 ** attempt) * 60 + random.uniform(0, 10)
            print(f"\n      [{control.id}] Rate limit — waiting {wait:.0f}s...", end=" ", flush=True)
            time.sleep(wait)

    if response is None:
        raise RuntimeError(f"No response from API after 3 attempts for {control.id}")

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {"verdict": "WARN", "findings": ["[response truncated — manual review required]"], "remediation": []}

    return Assessment(
        control_id=control.id,
        control_name=control.name,
        verdict=data.get("verdict", "N-A"),
        findings=data.get("findings", []),
        remediation=data.get("remediation", []),
    )


def assess(material: str, control: Control, client: anthropic.Anthropic) -> Assessment:
    """Assess a single control. Client must be provided by the caller."""
    return _call(client, material, control)


# Fix 4: parallel assessment — run all 10 controls concurrently
def assess_all(
    material: str,
    controls: list[Control],
    client: anthropic.Anthropic,
    on_result=None,
    max_workers: int = 5,
) -> list[Assessment]:
    """Assess all controls in parallel. on_result(assessment) called as each completes."""
    results: dict[str, Assessment] = {}

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_call, client, material, ctrl): ctrl for ctrl in controls}
        for future in as_completed(futures):
            a = future.result()
            results[a.control_id] = a
            if on_result:
                on_result(a)

    # Return in original control order
    return [results[ctrl.id] for ctrl in controls]
