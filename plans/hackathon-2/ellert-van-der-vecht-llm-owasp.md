# Plan Template — SAAF Hackathon Submission

---

## 1. Metadata

| Field | Value |
|---|---|
| **Submitter** | Mathijs Schouten (on behalf of Ellert van der Vecht) |
| **Organisation** | Schuberg Philis |
| **Session** | Hackathon 2 (Session 3) |
| **Type** | Workflow |
| **Status** | Draft |

---

## 2. Problem Statement

Organizations deploying LLM-based agents lack a repeatable, evidence-based way to assess their security posture against the OWASP Top 10 for LLM Applications. Manual audits are slow, inconsistent, and do not scale across the 45+ organizations in the SAAF community. This project provides an automated audit pipeline that any team can point at an agent's codebase, configuration, or architecture description and receive a scored, actionable report — covering all 10 OWASP LLM controls (LLM01–LLM10, 2025 edition).

---

## 3. Use-Case Type and Scope

**Audit domain:** AI Security / LLM Application Risk Assessment

**Applicable standards:**

- OWASP Top 10 for LLM Applications (2025) — LLM01 through LLM10
- ISO 27001 (A.12 — Operations security; A.14 — System acquisition, development and maintenance)

**In scope:**

- Collecting and normalizing audit material from agent codebases, config files, or architecture descriptions
- Assessing a target against all 10 OWASP LLM controls via Claude API
- Producing a scored Markdown report (PASS/FAIL/WARN/N-A per control) with findings and remediation advice
- Entry via CLI, Claude Code `/audit` slash command, or subagent dispatch

**Out of scope:**

- Runtime penetration testing or active exploitation
- Assessment of non-LLM applications
- Continuous monitoring (single-run assessment only in MVP)

---

## 4. SAAF 4-Pillar Mapping

| Pillar | What you will produce or reuse |
|---|---|
| **Prompts** | Per-control assessment prompts; OWASP control definitions in `docs/LLM01–LLM10.md` within the [llm_owasp repo](https://github.com/SAAF-Project/llm_owasp) |
| **Tools** | Python pipeline: `collector.py`, `controls.py`, `auditor.py`, `report.py`, `cli.py`, `claude_code.py` |
| **Regulatory** | OWASP LLM Top 10 (2025) control definitions — reusable as `regulatory/` input for AI system audits |
| **Outputs** | Scored Markdown audit report (`audit_report.md`) with scorecard table + per-control findings + remediation |

---

## 5. Prompts

### System prompt (draft — control assessor)

```
You are an AI security auditor specialised in the OWASP Top 10 for LLM Applications.
Given audit material (codebase, configuration, architecture description) and a single
OWASP LLM control definition, assess whether the target passes, fails, warns, or is
not applicable for this control.
Return a JSON object with: verdict (PASS/FAIL/WARN/N-A), findings (list of strings),
and remediation (list of actionable recommendations).
Base your assessment only on evidence present in the provided material.
Do not invent findings.
```

### Example user prompts

**Prompt 1 — LLM01 Prompt Injection:**
```
Control: LLM01 — Prompt Injection
Description: [OWASP LLM01 control text]
Audit material: [agent codebase / config / architecture description]

Assess whether this agent adequately mitigates prompt injection risks.
Return verdict, findings, and remediation in JSON.
```

**Prompt 2 — LLM06 Excessive Agency:**
```
Control: LLM06 — Excessive Agency
Description: [OWASP LLM06 control text]
Audit material: [agent codebase / config / architecture description]

Assess whether this agent has appropriate constraints on its permissions and actions.
Return verdict, findings, and remediation in JSON.
```

**Intended file location:** `prompts/audit-use-cases/llm-owasp-assessor.md`

---

## 6. Tools and Techniques

### Approach

The pipeline is a four-skill workflow with two human checkpoints:

1. **S1: material-collector** — reads target path (directory or file), normalizes source code + configs into a material bundle (50 KB/file limit, 500 KB total)
2. **S2: control-loader** — loads the 10 OWASP LLM control definitions from `docs/`
3. **S3: control-assessor** — calls Claude API once per control with material bundle + control definition; parses JSON verdict (PASS/FAIL/WARN/N-A), findings, remediation
4. **S4: report-formatter** — assembles a Markdown audit report with scorecard table and per-control detail

### Workflow with human checkpoints

| Step | Component | Checkpoint |
|---|---|---|
| 1 | S1: material-collector | **Human review** — verify no sensitive files included |
| 2–3 | S2 + S3: load + assess all 10 controls | Automatic |
| 4 | S4: report-formatter | **Human review** — confirm findings, approve or request re-assessment |
| 5 | Delivery | **Human sign-off** before sharing report |

### Example script or pseudocode

```python
# python -m owasp_llm_audit /path/to/agent/codebase
from owasp_llm_audit.collector import Collector
from owasp_llm_audit.controls import load_controls
from owasp_llm_audit.auditor import Auditor
from owasp_llm_audit.report import format_report

material = Collector().collect("/path/to/agent")
controls = load_controls("docs/")
assessments = [Auditor().assess(material, ctrl) for ctrl in controls]
print(format_report(assessments))
```

**Tech stack used:** Python 3.11+, Claude API (claude-sonnet-4-6), `anthropic` SDK, Hatchling (pyproject.toml)

**Intended file location:** `tools/scripts/llm-owasp/` (reference [llm_owasp repo](https://github.com/SAAF-Project/llm_owasp))

---

## 7. Regulatory and Policies

### Applicable standards

| Standard | Relevant controls |
|---|---|
| OWASP LLM01 | Prompt Injection |
| OWASP LLM02 | Sensitive Information Disclosure |
| OWASP LLM03 | Supply Chain |
| OWASP LLM04 | Data and Model Poisoning |
| OWASP LLM05 | Improper Output Handling |
| OWASP LLM06 | Excessive Agency |
| OWASP LLM07 | System Prompt Leakage |
| OWASP LLM08 | Vector and Embedding Weaknesses |
| OWASP LLM09 | Misinformation |
| OWASP LLM10 | Unbounded Consumption |

### Claude / AI tool usage notes

Audit material is limited to 500 KB total per run. No real PII or credentials should be included in the material sent to the API. The `--dry-run` flag generates a sample report without any API calls.

### Guardrails checklist

- [x] No `rm`, `sudo`, `curl`, `wget`, or `ssh` in scripts
- [x] No runtime `pip install`
- [x] Python scripts run only from `tools/scripts/`
- [x] No real audit evidence, credentials, or personal data committed
- [x] API keys loaded from environment variables only

---

## 8. Output Format and Examples

**Format:** Markdown (`audit_report.md`)

**Schema reference:** Output maps to `outputs/schemas/finding-schema.json` — each per-control finding can be expressed as a SAAF finding with id (LLM01–LLM10), title, risk_rating (FAIL=High, WARN=Medium), observation, recommendation.

### Synthetic example output

```json
{
  "id": "F-LLM06",
  "title": "Excessive Agency — agent has unrestricted file-write permissions",
  "risk_rating": "High",
  "observation": "The agent's tool configuration grants write access to the entire filesystem without scope constraints. No human approval step is required before file modification actions.",
  "recommendation": "Restrict file-write tool to a designated output directory. Add a human-in-the-loop checkpoint before any destructive file operation."
}
```

---

## 9. Tech Stack

**MVP scope:**

- [x] Claude API (claude-sonnet-4-6)
- [x] Python 3.11+
- [x] GitHub (fork + PR)
- [ ] Strapi (synthetic data API — optional)

**Stretch goals:**

- [ ] Parallel control assessment (reduce wall-clock time)
- [ ] Custom org-specific controls beyond OWASP Top 10
- [ ] Diff-mode audit (git diff — assess only changed files)
- [ ] Multi-agent comparative scorecard

---

## 10. Collaboration and Knowledge Sharing

**What I plan to open-source:**

- Full pipeline (collector, controls, auditor, report formatter)
- All 10 OWASP LLM control definition files (`docs/LLM01–LLM10.md`)
- Claude Code `/audit` slash command integration

**What help I'm looking for:**

- Unit tests for all four skill modules (P0 priority)
- CI pipeline (GitHub Actions — lint, test, dry-run on PRs)
- Input from security-focused organizations on control interpretation edge cases

**Cross-org interest:**

Every SAAF organization building AI agents needs a way to assess those agents against OWASP LLM risks. The S3 control-assessor skill is independently composable into any existing audit agent. The OWASP control definitions in `docs/` are reusable as a knowledge base across the community.

**Related SAAF plans:**

- [`plans/hackathon-3/icfcop-control-testing-agent.md`](../hackathon-3/icfcop-control-testing-agent.md) — ICFCOP multi-framework control testing; complements this plan's LLM-specific assessments with broader compliance framework coverage
- [`plans/hackathon-3/saaf-rag-knowledge-base.md`](../hackathon-3/saaf-rag-knowledge-base.md) — the OWASP LLM control definitions (`docs/LLM01–LLM10.md`) are candidate RAG corpus documents

**Gandalf AI-Hacking Exercise:**

The [Gandalf AI-hacking exercise](https://gandalf.lakera.ai/) is a hands-on prompt injection challenge directly relevant to **LLM01 (Prompt Injection)**. In the Gandalf exercise, participants attempt to extract a secret password from an LLM that has been instructed not to reveal it — progressively harder across 8 levels. This is an excellent practical complement to the automated LLM01 assessment: after the tool flags a prompt injection risk (FAIL or WARN), the Gandalf exercise demonstrates concretely how real attackers exploit the same vulnerability.

Recommended use in SAAF context:
- Run the OWASP audit pipeline against an agent's codebase to identify LLM01 vulnerabilities
- Use Gandalf levels 1–4 as a practical demonstration for auditees: "This is what prompt injection looks like in practice"
- Include Gandalf completion screenshots as supporting evidence in the audit workpaper
- Note: levels 7–8 require advanced jailbreaking techniques; levels 1–4 are sufficient for audit demonstration purposes

**Real-World Prompt Injection in Skill Ecosystems:**

Beyond direct user-to-agent injection, a more insidious pattern emerges in multi-agent skill ecosystems: **indirect prompt injection via skill outputs**. When Agent A calls Agent B's skill and trusts the returned output as safe context, a compromised or malicious skill can inject instructions into Agent A's context window without the user's knowledge. This is architecturally identical to LLM01 but occurs at the agent-to-agent layer.

Audit implications:
- Any SAAF agent that chains multiple skills (e.g., RAG KB → MCP tool → evidence agent) is potentially vulnerable to this pattern
- The OWASP audit pipeline should be extended to test multi-skill chains, not just single-agent inputs
- Mitigation: treat all skill outputs as untrusted input; apply output sanitization before passing between agents
- Document this risk in Section 7 (Regulatory) of any plan that uses skill chaining

**OWASP AI Testing Guide v1.0 (250-page full reference):**

The [OWASP AI Testing Guide v1.0](https://github.com/OWASP/www-project-ai-testing-guide) — a 250-page living document — substantially extends the OWASP LLM Top 10 coverage of this plan. Where the Top 10 provides risk categories, the AI Testing Guide provides **operational test procedures** (AT-01 through AT-12) that an auditor can execute against a deployed AI system:

| Test ID | Test Name | Relation to LLM Top 10 |
|---|---|---|
| AT-01 | Prompt Injection | LLM01 |
| AT-02 | Training Data Poisoning | LLM03 |
| AT-03 | Model Inversion / Extraction | LLM08 |
| AT-04 | Adversarial Examples | LLM09 |
| AT-05 | Supply Chain Integrity | LLM03 |
| AT-06 | Sensitive Information Disclosure | LLM02 |
| AT-07 | Excessive Agency | LLM06 |
| AT-08 | Overreliance / Hallucination | LLM09 |
| AT-09 | Privacy Violations | LLM02 |
| AT-10 | Denial of Model Service | LLM10 |
| AT-11 | Model Bias and Fairness | New (not in Top 10) |
| AT-12 | Explainability and Transparency | New (not in Top 10) |

The companion plan [`plans/hackathon-3/owasp-ai-testing-agent.md`](../hackathon-3/owasp-ai-testing-agent.md) operationalizes the full AI Testing Guide as an automated audit agent. The two plans are complementary: this plan covers LLM Top 10 assessment of an agent's codebase; the AI Testing Agent covers operational testing against a running AI system.

**Abliteration / Heretic Attack Vector:**

A novel attack vector relevant to **LLM01 (Prompt Injection)** and **LLM06 (Excessive Agency)** emerged in early 2025: **directional ablation** (also called "abliteration" or "uncensoring") via the open-source tool [Heretic](https://github.com/p-e-w/heretic). This technique:

1. Identifies the "refusal direction" in a model's residual stream using contrastive activation pairs (refused vs. complied requests)
2. Projects out the refusal direction from all attention heads and MLP layers
3. Produces a modified model that no longer refuses requests — regardless of safety alignment training

**Audit implications for SAAF:**
- Any organization that self-hosts an open-weight model (Llama, Mistral, Qwen) and allows external or untrusted model sources must assess whether the model has been abliterated
- The OWASP audit pipeline should add a check: does the deployed model refuse a set of known-harmful test prompts? If not, the model may have been modified
- For audit use cases: abliterated models pose risk if used in agents with tool access — they will comply with injected instructions that a safety-aligned model would refuse
- Add to LLM01 test suite: "safety alignment verification" — 10 graduated test prompts verifying the model still refuses known harmful requests

**Enterprise AI Visibility Context (Akto 2025):**

According to Akto's 2025 State of Agentic AI Security report, **only 21% of enterprises have visibility into their own AI agents** — meaning 79% have undocumented agents running in production without audit coverage. This statistic is directly relevant to this plan:

- The OWASP LLM audit pipeline can only assess agents the organization knows about
- Pre-condition for any LLM audit: run the [`ai-agent-visibility-scanner.md`](../hackathon-3/ai-agent-visibility-scanner.md) to discover all agents first
- The 21% visibility stat is a powerful finding for internal audit reports: "Prior to this audit, the organization had visibility into X% of its AI agents" (benchmarked against the 21% industry baseline)

---

## 11. PDCA Positioning

| Phase | Status for this plan | Notes |
|---|---|---|
| **Plan** | Complete | Original plan written March 24, 2026; converted to SAAF template here |
| **Do** | Complete | Working prototype built; `audit_report.md` generated from own codebase |
| **Check** | Not started | Planned: use against SAAF community agent repos |
| **Act** | Not started | Target: Hackathon 3 — share learnings, add parallel assessment |

---

## 12. Open Questions

1. Should control assessment run in parallel (10 concurrent Claude calls) for speed, or sequentially for easier debugging?
2. How should the tool handle agent targets that have no codebase — only a running API endpoint or a deployment config?
3. Is there interest in a shared OWASP LLM controls library maintained by the SAAF community, so all organizations can contribute updated control definitions?
