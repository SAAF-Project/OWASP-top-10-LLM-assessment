"""Core audit logic — builds the prompt, calls Claude, returns structured results."""

import json
from pathlib import Path

import anthropic

from owasp_llm_audit.collector import collect
from owasp_llm_audit.controls import load_controls, load_control_ids
from owasp_llm_audit.report import format_report

AUDIT_SYSTEM_PROMPT = """\
You are an expert AI security auditor specializing in the OWASP Top 10 for LLM Applications (2025).

You will receive:
1. The OWASP LLM Top 10 control definitions
2. Material describing an AI agent (source code, config files, architecture description, or a mix)

Your job: assess the agent against each of the 10 OWASP LLM controls.

For each control, provide:
- "id": The control ID (e.g. "LLM01")
- "name": The control name
- "status": One of "PASS", "FAIL", "WARN", "N/A"
  - PASS: The agent adequately addresses this risk
  - FAIL: The agent has a clear vulnerability or gap for this risk
  - WARN: Potential concern that needs further investigation
  - N/A: This control does not apply to this agent's architecture
- "findings": A list of specific observations (strings)
- "remediation": A list of recommended actions (strings), empty if PASS

Respond ONLY with valid JSON in this format:
{
  "summary": "One paragraph overall assessment",
  "controls": [
    {
      "id": "LLM01",
      "name": "Prompt Injection",
      "status": "FAIL",
      "findings": ["The agent passes raw user input directly to the system prompt...", ...],
      "remediation": ["Implement input validation and sanitization...", ...]
    },
    ...
  ]
}
"""


DRY_RUN_RESULT = {
    "summary": (
        "This audit tool itself has moderate exposure across several OWASP LLM controls. "
        "As an agent that calls the Claude API with user-supplied content, it faces prompt injection risks. "
        "The collector reads arbitrary filesystem paths without sandboxing. Output handling trusts the "
        "LLM response JSON without strict schema validation. The tool has limited agency (no write operations "
        "beyond report files), which is good. Supply chain risk is low given minimal dependencies."
    ),
    "controls": [
        {
            "id": "LLM01", "name": "Prompt Injection", "status": "WARN",
            "findings": [
                "User-supplied file content is embedded directly into the audit prompt without sanitization",
                "Malicious code in audited files could attempt to manipulate audit results",
                "No input filtering or prompt armoring is applied to collected material",
            ],
            "remediation": [
                "Add content sanitization to collector.py before embedding in prompts",
                "Implement prompt armoring with clear delimiters between instructions and user content",
                "Consider a two-pass approach: sanitize first, then audit",
            ],
        },
        {
            "id": "LLM02", "name": "Sensitive Information Disclosure", "status": "WARN",
            "findings": [
                "The collector reads .env.example files and could read files containing secrets",
                "Collected file content is sent to the Claude API — any secrets in source files will be transmitted",
                "No redaction of API keys, tokens, or credentials before sending to the API",
            ],
            "remediation": [
                "Add a secrets scanner to collector.py that redacts common patterns (API keys, tokens)",
                "Exclude .env files and known credential file patterns from collection",
                "Warn users when potentially sensitive files are detected",
            ],
        },
        {
            "id": "LLM03", "name": "Supply Chain", "status": "PASS",
            "findings": [
                "Minimal dependency footprint — only the anthropic SDK",
                "Uses pyproject.toml with pinned minimum versions",
                "No pre-trained models or LoRA adapters in use",
            ],
            "remediation": [],
        },
        {
            "id": "LLM04", "name": "Data and Model Poisoning", "status": "N/A",
            "findings": [
                "This tool does not train or fine-tune models",
                "OWASP control docs are static local files under version control",
            ],
            "remediation": [],
        },
        {
            "id": "LLM05", "name": "Improper Output Handling", "status": "WARN",
            "findings": [
                "LLM response is parsed as JSON without strict schema validation",
                "If JSON parsing fails, the error is unhandled and crashes the tool",
                "Report output is written directly to disk without path validation",
            ],
            "remediation": [
                "Add JSON schema validation for the audit response",
                "Implement graceful error handling for malformed LLM responses",
                "Validate and sanitize the output file path",
            ],
        },
        {
            "id": "LLM06", "name": "Excessive Agency", "status": "PASS",
            "findings": [
                "The tool only reads files and writes a single report — minimal agency",
                "No database connections, network calls (beyond API), or shell execution",
                "No ability to modify the audited codebase",
            ],
            "remediation": [],
        },
        {
            "id": "LLM07", "name": "System Prompt Leakage", "status": "PASS",
            "findings": [
                "System prompt contains no secrets or credentials",
                "System prompt is visible in source code (open source) — no security-through-obscurity",
                "No sensitive operational parameters in the prompt",
            ],
            "remediation": [],
        },
        {
            "id": "LLM08", "name": "Vector and Embedding Weaknesses", "status": "N/A",
            "findings": [
                "No RAG, vector database, or embedding pipeline is used",
                "OWASP controls are loaded as plain text files, not embeddings",
            ],
            "remediation": [],
        },
        {
            "id": "LLM09", "name": "Misinformation", "status": "WARN",
            "findings": [
                "Audit findings are LLM-generated and could contain false positives or negatives",
                "No cross-verification or confidence scoring is applied to results",
                "Users may treat the report as authoritative without independent verification",
            ],
            "remediation": [
                "Add a disclaimer to reports that findings are AI-generated and should be verified",
                "Consider a multi-pass audit with different prompts to cross-check findings",
                "Add confidence scores to each control assessment",
            ],
        },
        {
            "id": "LLM10", "name": "Unbounded Consumption", "status": "WARN",
            "findings": [
                "No token budget or cost estimation before making API calls",
                "Large codebases could generate very large prompts with high token costs",
                "MAX_TOTAL_SIZE limit exists (500K chars) but no token-based limit",
            ],
            "remediation": [
                "Add token estimation and display expected cost before calling the API",
                "Add a --max-tokens flag to let users set a budget",
                "Warn when collected material exceeds a cost threshold",
            ],
        },
    ],
}


def run_audit(
    target: str,
    docs_dir: Path | None = None,
    model: str = "claude-sonnet-4-6",
    output_path: str | None = None,
    dry_run: bool = False,
    control_id: str | None = None,
) -> str:
    """Run an OWASP LLM audit against a target.

    Args:
        target: File path, directory path, or text description of the agent.
        docs_dir: Override path to OWASP control docs.
        model: Claude model to use for the audit.
        output_path: If provided, write the report to this file.
        dry_run: If True, return a sample report without calling the API.

    Returns:
        The formatted markdown report.
    """
    # 1. Collect material from target
    material = collect(target)

    # 2. Load OWASP controls (all or single)
    controls_text = load_controls(docs_dir, control_id=control_id)
    control_ids = load_control_ids()
    if control_id:
        control_ids = [c for c in control_ids if c["id"].upper() == control_id.upper()]

    if dry_run:
        audit_result = DRY_RUN_RESULT
    else:
        # 3. Build the user prompt
        scope = f"only the {control_id} control" if control_id else "all 10 OWASP LLM controls"
        user_prompt = f"""\
## OWASP LLM Control Definition(s)

{controls_text}

---

## Agent Material to Audit

{material}

---

Assess this agent against {scope}. Return your assessment as JSON.
"""

        # 4. Call Claude
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=model,
            max_tokens=8192,
            system=AUDIT_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        # 5. Parse response
        response_text = response.content[0].text
        json_text = response_text
        if "```json" in json_text:
            json_text = json_text.split("```json")[1].split("```")[0]
        elif "```" in json_text:
            json_text = json_text.split("```")[1].split("```")[0]

        audit_result = json.loads(json_text.strip())

    # 6. Format report
    report = format_report(audit_result, target)

    # 7. Optionally write to file
    if output_path:
        Path(output_path).write_text(report)

    return report
