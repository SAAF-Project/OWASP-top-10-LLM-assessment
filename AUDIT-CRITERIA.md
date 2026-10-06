# `AUDIT-CRITERIA.md`

## Metadata

| Field | Value |
|---|---|
| **Agent** | OWASP Top 10 LLM Assessment |
| **Repository** | https://github.com/SAAF-Project/OWASP-top-10-LLM-assessment |
| **Maintainer(s)** | SAAF Project |
| **Last reviewed** | 2026-09-15 |
| **Status** | Draft |
| **Branch described** | `main` (origin/HEAD) plus the changes in PR #3 |

> **Branch notice:** `main`, `master` and `feature/audit-criteria` have diverged (`master` carries an older lineage; a local `agents/run-claude-integration` branch also exists). This document describes `main` + PR #3 only.
>
> **Agent type:** All tools make live Anthropic Claude API calls at runtime (`claude-opus-4-6`), so AI-specific frameworks apply.
>
> **Sources used to draft this document:** `README.md`, `CLAUDE.md`, `assessment-methodology.md`, `llm-owasp/` docs, and the existing Session 6 A2 draft.

## 1. What the agent does

Reviews AI agent source code and configuration files against the OWASP Top 10 for LLM Applications (2025 edition). Takes a file or folder of agent artefacts as input and produces a structured per-control verdict (PASS / WARN / FAIL / N/A) plus an overall risk rating (Critical / High / Medium / Low). Available as a CLI, a Flask web portal, and a full audit pipeline package.

## 2. Control objectives & framework mapping

| Control objective | Framework + clause/area | Why relevant |
|---|---|---|
| CO-1 — LLM-based agents are assessed for prompt injection vulnerabilities before deployment | OWASP LLM01 (2025) | Prompt injection is the leading attack vector against LLM applications |
| CO-2 — Agents do not expose sensitive information or credentials through outputs, logs, or prompts | OWASP LLM02 (2025) · GDPR Art. 25 (data minimisation) | Prevents PII leakage and credential theft |
| CO-3 — Agent supply chains (dependencies, models, plugins) are verified, pinned, and monitored | OWASP LLM03 (2025) · ISO 27001 (Third-Party & Vendor Risk) | Unverified dependencies are a primary compromise vector |
| CO-4 — Agents operate under least privilege and require human authorisation for irreversible actions | OWASP LLM06 (2025) · EU AI Act · NIST AI RMF | Limits blast radius of agent misbehaviour |
| CO-5 — LLM-generated outputs are validated before being rendered, executed, or passed to downstream systems | OWASP LLM05 (2025) | Prevents XSS, SQL injection, and code execution from model output |
| CO-6 — Agents have resource controls to prevent unbounded API consumption and cost overruns | OWASP LLM10 (2025) | Protects against denial-of-wallet and runaway agentic loops |
| CO-7 — The reviewer's own findings are grounded and traceable: no fabricated findings, every non-N/A verdict cites file + line | EU AI Act (Art. 13 transparency) · NIST AI RMF (Measure) | An auditing agent that invents or cannot evidence findings misleads the auditor |
| CO-8 — The reviewer states its uncertainty and requires human review before results are relied upon | EU AI Act (Art. 14 human oversight) · IIA Standards | Prevents LLM output being treated as audit-ready |

*Full framework catalogue: `docs/reference/domains-and-frameworks.md` in the SAAF-Project repo.*

## 3. Acceptance criteria (testable, pass/fail)

**CO-1 — Prompt Injection**
- Given an agent file, the tool identifies whether system prompt and user input are structurally separated at the API level.
- Given raw user input concatenated into the system prompt, the tool returns FAIL for LLM01.
- Given an agent with no user input and hardcoded prompts only, the tool returns N/A for LLM01.

**CO-2 — Sensitive Information Disclosure**
- Given an agent file containing a hardcoded API key or secret, the tool returns FAIL for LLM02.
- Given an agent that sends full user records to the model without redaction, the tool returns FAIL for LLM02.
- Given an agent that loads secrets from environment variables only, the tool returns PASS for criterion 2.1.

**CO-3 — Supply Chain**
- Given a project with no version-pinned dependencies and no lockfile, the tool returns FAIL for LLM03.
- Given a project with all dependencies pinned and a lockfile present, the tool returns PASS for criterion 3.1.
- The tool never returns N/A for LLM03 regardless of agent architecture.

**CO-4 — Excessive Agency**
- Given an agent that performs irreversible actions (delete, send, publish) without a human confirmation step, the tool returns FAIL for LLM06.
- Given a read-only agent with no tools and no API calls, the tool returns N/A for LLM06.
- Given an agent with no iteration cap on agentic loops, the tool returns FAIL for criterion 6.3.

**CO-5 — Improper Output Handling**
- Given model output passed to `eval()`, `exec()`, or `subprocess` with no sandboxing, the tool returns FAIL for LLM05.
- Given model output interpolated into raw SQL without parameterisation, the tool returns FAIL for criterion 5.3.
- Given an agent that renders model output as raw HTML with no escaping, the tool returns FAIL for criterion 5.1.

**CO-6 — Unbounded Consumption**
- Given an API call with no `max_tokens` set, the tool returns FAIL for LLM10.
- Given an agent with no iteration limits on loops, the tool returns FAIL for criterion 10.2.
- The tool never returns N/A for LLM10 regardless of agent architecture.

**CO-7 — Grounded, traceable findings**
- Given a submitted file, every FAIL/WARN verdict includes a file path and line number that exist in the input.
- Given an input containing no vulnerable pattern for a control, the tool does not return FAIL for it.
- Limitation, stated honestly: line-number accuracy is produced by the model and is not programmatically verified against the source.

**CO-8 — Uncertainty and human review**
- Given an inference not directly evidenced in the code, the output labels it as an inference rather than a confirmed finding.
- Given any completed review, the output does not claim to be audit-ready or certified.
- Limitation, stated honestly: the human-review gate is a wording convention in the output, not an enforced workflow step.

## 4. Good output / never do

| A correct output MUST contain | The agent must NEVER |
|---|---|
| ✓ A verdict (PASS / WARN / FAIL / N/A) for each of the 10 OWASP LLM controls | ✕ Invent findings not grounded in the submitted source code or config |
| ✓ File path and line number evidence for every non-N/A verdict | ✕ Present output as audit-ready without a human-review gate |
| ✓ An overall risk rating (Critical / High / Medium / Low) derived from the aggregation rules in `assessment-methodology.md` | ✕ Hard-code credentials or API keys in source, prompts, or config |
| ✓ `llm-owasp` appends a machine-readable JSON block conforming to `outputs/schemas/finding-schema.json` for every FAIL/WARN verdict | ✕ Return N/A for LLM03 or LLM10 (these controls are never N/A) |
| ✓ Confidence language that distinguishes evidence-backed findings from inferences | ✕ Return N/A for LLM09 in any audit context |

## 5. Coverage gaps

- **No dynamic / runtime analysis** — the tool performs static analysis only. Prompt injection via runtime tool outputs is not detectable from source code alone.
- **LLM04 (Data and Model Poisoning)** — criteria require access to training pipelines and RAG ingestion processes that are rarely in scope of a single agent file review.
- **LLM08 (Vector and Embedding Weaknesses)** — tenant isolation and write-access controls on vector stores cannot be verified from agent source code without access to infrastructure configuration.
- **No end-to-end acceptance tests** — `llm-owasp` has unit tests (`tests/`) but they mock the Claude API and test pipeline mechanics only, not whether the tool correctly detects real vulnerabilities. Neither tool has tests that run against `prototype/test_agent.py` or any real insecure agent. `agent-reviewer/` has no test suite at all.
- **Multi-file dependency tracing** — the tool does not resolve cross-file imports, so secrets or unsafe patterns in imported modules may not be detected.

## 6. Status / validation

| Acceptance criterion | Verified? | Evidence |
|---|---|---|
| CO-1 #1 — Structural separation detected | ☑ | 2026-10-06 run on `prototype/test_agent.py`: reported no `system`/`user` role separation. Positive case only; the "separated" case was not tested |
| CO-1 #2 — FAIL on concatenated prompt | ☑ | Same run: LLM01 = FAIL for the f-string prompt (real lines 12–13) |
| CO-2 #1 — FAIL on hardcoded API key | ☑ | Same run: LLM02 = FAIL, flagged `API_KEY` (real line 8). Note the value is a placeholder string, not a real key |
| CO-3 #3 — Never N/A for LLM03 | ☑ | First run returned N/A ("no imports"); fixed by a "never N/A" rule in the system prompt. Re-run twice on `test_agent.py`: LLM03 = WARN (no manifest, lockfile or model pinning) |
| CO-4 #1 — FAIL on no human checkpoint | ☐ | Not exercised: `test_agent.py` performs no irreversible actions (LLM06 = PASS). Needs a different test agent |
| CO-5 #1 — FAIL on eval/exec with model output | ☐ | Not exercised: `test_agent.py` has no `eval`/`exec`/`subprocess`. LLM05 = FAIL was given for a plain `print`, which is stricter than the criterion |
| CO-6 #1 — FAIL on missing max_tokens | ☑ | First run returned WARN because the LLM call is a stub; fixed by a prompt rule that stub calls count as call sites. Re-run twice on `test_agent.py`: LLM10 = FAIL. Not tested against a real API call |
| CO-6 #3 — Never N/A for LLM10 | ☑ | Same run: LLM10 = WARN (not N/A). Single run only |
| CO-7 #1 — Cited file/line exists in input | ☑ | First run: cited lines 9, 14–15, 21 and 26 were wrong (real: 8, 12–13, 19, 25), the review date was fabricated and LLM08 was missing from the summary. Fixed: source is sent with `N\| ` line prefixes, the prompt forbids writing a date and requires all ten controls, and `verify_citations()` checks every cited line and quote against the file. Re-run twice: cited lines correct, 14 citations machine-verified in the last run |
| CO-8 #2 — No audit-ready claim in output | ☑ | Same run: no audit-ready or certified claim. Single run only; the review stops short of a human-review notice, which is a gap |

Overall status: **Draft** — first validation run 2026-10-06 against `prototype/test_agent.py` (`agent-reviewer/review_agent.py`, `claude-opus-4-6`): 8 criteria verified (three of them, CO-3 #3, CO-6 #1 and CO-7 #1, only after tool fixes made the same day), 2 not exercised (CO-4 #1, CO-5 #1). All results come from one small sample (3 runs), so they are indicative only. Verdicts are not fully deterministic: LLM06 and LLM07 changed between the first and later runs (PASS to WARN, WARN to FAIL), and CO-7 is still limited, since the citation check cannot catch a wrong-but-real line.

## 7. Observability

- **Logged today:** the Flask portal appends each completed review to `audit_log.jsonl` (gitignored). CLI tools write reports to stdout and, in folder mode, to `<folder>/reports/`.
- **Missing:** no structured run log or tracing for the CLIs or `llm-owasp`, no token/cost tracking, no record of model version or prompt hash per review, and `audit_log.jsonl` is local-only with no retention policy.
