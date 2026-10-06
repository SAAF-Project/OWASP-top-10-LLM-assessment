"""Assess audit material against OWASP LLM controls via Claude API."""
from __future__ import annotations
import json
import random
import re
import time
import anthropic
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

# Fix 1: import using package-relative path so the module works from any cwd
from .controls import Control

MODEL = "claude-opus-4-6"

SYSTEM_PROMPT = """\
You are an AI security auditor specialised in the OWASP Top 10 for LLM Applications (2025 edition).
Given audit material (agent plan, codebase, configuration, or architecture description) and a single
OWASP LLM control definition, assess whether the target passes, fails, warns, or is not applicable
for this control.

## Verdict definitions

- PASS: All required mitigations are present in the code, configuration, or architecture. No
  indicators of the risk were detected. Minor improvements may still be possible.
- WARN: Some mitigations are present but gaps remain. The risk is reduced but not eliminated.
  Specific remediation actions can close the gap.
- FAIL: One or more indicators of the risk are present in the code with no corresponding
  mitigation. The agent is exposed to the described attack or failure mode.
- N-A: The agent's architecture makes the risk category irrelevant (e.g., no RAG for LLM08,
  no fine-tuning for LLM04). Requires positive evidence that the capability is absent —
  if uncertain, default to WARN.

## Verdict escalation

- A single FAIL finding on any criterion within a control makes the overall control verdict FAIL.
- A control with mixed PASS and WARN findings is WARN.

## Controls that are never N-A

- LLM03 Supply Chain: NEVER N-A. Every agent has a supply chain. Having no imports or no
  requirements file is not evidence of safety: absent dependency pinning, a lockfile, or
  model/provider version pinning is itself a gap (WARN, or FAIL if dependencies exist unpinned).
- LLM09 Misinformation: NEVER N-A in an audit context.
- LLM10 Unbounded Consumption: NEVER N-A. Treat a stub, mock, or placeholder LLM call as a real
  call site: if it has no max_tokens and no input length cap, the verdict is FAIL. Do not
  downgrade to WARN because the call is a stub.

## Evidence standard

Source files are supplied with each line prefixed by its 1-based line number as `N| `. Cite those
numbers exactly. Never include the `N| ` prefix inside quoted code, and never estimate or guess a
line number.

Every finding MUST cite:
1. Location — file path and line number(s) where the evidence was found (or where the expected
   mitigation is absent). Use the format "file.py:42".
2. Observation — what was found or not found, stated as fact.
3. Reasoning — why this observation maps to the given verdict.

Findings without file-level evidence must be flagged as "[no direct evidence — manual review required]".

## Response format

Return ONLY a valid JSON object with these fields:
- verdict: one of PASS, FAIL, WARN, N-A
- findings: list of strings, each citing location and observation (empty list for PASS/N-A)
- remediation: list of actionable recommendation strings (empty list for PASS/N-A)

Base your assessment ONLY on evidence present in the provided material. Do not invent findings.
Assessment methodology version: 1.0
"""


@dataclass
class Assessment:
    control_id: str
    control_name: str
    verdict: str          # PASS | FAIL | WARN | N-A
    findings: list[str]
    remediation: list[str]


# Controls that can never be N-A (assessment-methodology.md); enforced in code, not only in the prompt.
NEVER_NA = frozenset({"LLM03", "LLM09", "LLM10"})

_CITE_RE = re.compile(r"([\w.\-/\\]+\.\w+):(\d+)(?:-(\d+))?")
_QUOTE_RE = re.compile(r"`([^`]{4,})`")


def _finding_text(item) -> str:
    """The model sometimes returns a finding as an object instead of a string; flatten it."""
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return "; ".join(f"{k}: {v}" for k, v in item.items())
    return str(item)


def verify_findings(findings: list[str], sources: dict[str, str]) -> tuple[list[str], int]:
    """Check file:line citations (and any `quoted` code) in findings against the real sources.

    Returns (findings, checked): each finding whose citation does not match the source gets a
    "[citation unverified: ...]" suffix; checked counts the citations that matched or failed.
    """
    lines_by_name = {Path(n).name: t.splitlines() for n, t in sources.items()}
    text_by_name = {Path(n).name: t for n, t in sources.items()}
    out: list[str] = []
    checked = 0
    for finding in findings:
        problems: list[str] = []
        for m in _CITE_RE.finditer(finding):
            name = Path(m.group(1)).name
            src = lines_by_name.get(name)
            if src is None:
                continue  # not one of the submitted files (e.g. a library name like os.path:)
            start, end = int(m.group(2)), int(m.group(3) or m.group(2))
            checked += 1
            if start < 1 or end > len(src) or start > end:
                problems.append(f"{name}:{start}-{end} is outside the file ({len(src)} lines)")
                continue
            cited = "\n".join(src[start - 1:end])
            for q in _QUOTE_RE.findall(finding):
                # Findings are prose, so only judge quotes that look like code (contain whitespace)
                # and occur verbatim elsewhere in the file: that is a real line quoted at the wrong
                # location. Identifiers and paraphrases (`call_llm`, `input()`) are descriptions.
                if len(q) >= 8 and re.search(r"\s", q) and q in text_by_name[name] and q not in cited:
                    problems.append(f"{name}:{start}-{end} does not contain `{q[:50]}`")
        out.append(finding + (f" [citation unverified: {'; '.join(problems)}]" if problems else ""))
    return out, checked


# Fix 2: client created once and passed in; assess() is pure
def _call(client: anthropic.Anthropic, material: str, control: Control,
          sources: dict[str, str] | None = None) -> Assessment:
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

    verdict = data.get("verdict", "N-A")
    findings = [_finding_text(f) for f in data.get("findings", [])]
    if control.id in NEVER_NA and verdict == "N-A":
        verdict = "WARN"
        findings.append(f"[verdict overridden: {control.id} can never be N-A — manual review required]")
    if sources:
        findings, _ = verify_findings(findings, sources)

    return Assessment(
        control_id=control.id,
        control_name=control.name,
        verdict=verdict,
        findings=findings,
        remediation=data.get("remediation", []),
    )


def assess(material: str, control: Control, client: anthropic.Anthropic,
           sources: dict[str, str] | None = None) -> Assessment:
    """Assess a single control. Client must be provided by the caller.

    sources: optional {filename: text} (see collector.collect_sources) used to verify citations.
    """
    return _call(client, material, control, sources)


# Fix 4: parallel assessment — run all 10 controls concurrently
def assess_all(
    material: str,
    controls: list[Control],
    client: anthropic.Anthropic,
    on_result=None,
    max_workers: int = 5,
    sources: dict[str, str] | None = None,
) -> list[Assessment]:
    """Assess all controls in parallel. on_result(assessment) called as each completes."""
    results: dict[str, Assessment] = {}

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_call, client, material, ctrl, sources): ctrl for ctrl in controls}
        for future in as_completed(futures):
            a = future.result()
            results[a.control_id] = a
            if on_result:
                on_result(a)

    # Return in original control order
    return [results[ctrl.id] for ctrl in controls]
