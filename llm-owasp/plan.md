# SAAF Plan: OWASP LLM Audit Agent

## Metadata

| Field | Value |
|-------|-------|
| **Plan name** | OWASP LLM Top 10 Audit Agent |
| **Use-case type** | Workflow (orchestrated sequence of agents and skills with human checkpoints) |
| **Author** | Evan de Rvecht |
| **Date** | 2026-03-24 |
| **Status** | Initial Setup |
| **OWASP controls covered** | LLM01–LLM10 (full Top 10 for LLM Applications 2025) |

---

## 1. Problem Statement

Organizations deploying LLM-based agents lack a repeatable, evidence-based way to assess their security posture against the OWASP Top 10 for LLM Applications. Manual audits are slow, inconsistent, and don't scale across the 45+ organizations in the SAAF community. This project provides an automated audit pipeline that any team can point at an agent's codebase, configuration, or architecture description and receive a scored, actionable report.

---

## 2. Components

### 2.1 Skills

| # | Skill name | Purpose | Inputs | Outputs |
|---|-----------|---------|--------|---------|
| S1 | **material-collector** | Collect and normalize audit material from a target (codebase, config files, text descriptions) | Target path or stdin | Structured material bundle (source code, configs, directory tree) |
| S2 | **control-loader** | Load and parse the 10 OWASP LLM control definitions from `docs/` | Control docs directory | List of control objects (id, name, description, prevention measures) |
| S3 | **control-assessor** | Assess a single OWASP control against collected material via Claude API | Material bundle + single control definition | Per-control verdict: PASS / FAIL / WARN / N/A + findings + remediation |
| S4 | **report-formatter** | Format scored results into a markdown audit report with scorecard table and detailed findings | List of control assessments + metadata | Markdown report |

### 2.2 Agents

| # | Agent name | Purpose | Skills used | Tools called |
|---|-----------|---------|-------------|-------------|
| A1 | **owasp-llm-auditor** | End-to-end autonomous audit of a target against all 10 OWASP LLM controls | S1, S2, S3, S4 | Claude API (anthropic SDK), filesystem read, stdout/file write |

### 2.3 Workflow

| # | Workflow name | Purpose | Steps | Human checkpoints |
|---|-------------|---------|-------|-------------------|
| W1 | **full-audit-workflow** | Orchestrate a complete audit run with review gates | See Section 4 | Material review, report review |

---

## 3. Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Entry Points                       │
│  CLI  │  Claude Code /audit  │  Subagent dispatch    │
└───┬───┴──────────┬───────────┴───────────┬──────────┘
    │              │                       │
    ▼              ▼                       ▼
┌─────────────────────────────────────────────────────┐
│              S1: material-collector                   │
│  Reads target path → normalizes files → bundles      │
│  Limits: 50 KB/file, 500 KB total, skips noise dirs  │
└──────────────────────┬──────────────────────────────┘
                       │ material bundle
                       ▼
┌─────────────────────────────────────────────────────┐
│              S2: control-loader                       │
│  Reads docs/LLM01..LLM10 → structured controls      │
└──────────────────────┬──────────────────────────────┘
                       │ control definitions
                       ▼
┌─────────────────────────────────────────────────────┐
│           S3: control-assessor  (×10)                │
│  For each control: build prompt → call Claude API    │
│  → parse JSON verdict (PASS/FAIL/WARN/N/A)           │
└──────────────────────┬──────────────────────────────┘
                       │ assessment results
                       ▼
┌─────────────────────────────────────────────────────┐
│              S4: report-formatter                     │
│  Scorecard table + detailed findings + remediation   │
│  Output: Markdown to stdout or file                  │
└─────────────────────────────────────────────────────┘
```

---

## 4. Workflow Steps

### W1: full-audit-workflow

| Step | Component | Action | Checkpoint |
|------|-----------|--------|------------|
| 1 | **S1: material-collector** | Collect and normalize all audit material from the target | **Human review**: verify material is complete and no sensitive files are inadvertently included |
| 2 | **S2: control-loader** | Load OWASP LLM control definitions | Automatic |
| 3 | **S3: control-assessor** | Assess each of the 10 controls against the material | Automatic |
| 4 | **S4: report-formatter** | Generate scored markdown report | **Human review**: review findings, confirm accuracy, approve or request re-assessment of specific controls |
| 5 | Delivery | Write report to file or stdout | **Human sign-off**: final approval before sharing |

---

## 5. Implementation Map

Existing code already implements the core pipeline. The mapping to SAAF components:

| SAAF component | Current implementation | File(s) |
|---------------|----------------------|---------|
| S1: material-collector | `Collector` class | `owasp_llm_audit/collector.py` |
| S2: control-loader | `load_controls()` | `owasp_llm_audit/controls.py` |
| S3: control-assessor | `Auditor` class | `owasp_llm_audit/auditor.py` |
| S4: report-formatter | `format_report()` | `owasp_llm_audit/report.py` |
| A1: owasp-llm-auditor | CLI + Claude Code entry points | `owasp_llm_audit/cli.py`, `owasp_llm_audit/claude_code.py` |
| W1: full-audit-workflow | `main()` in CLI | `owasp_llm_audit/cli.py`, `owasp_llm_audit/__main__.py` |

---

## 6. OWASP Controls Covered

| Control ID | Control name | Doc file |
|-----------|-------------|----------|
| LLM01 | Prompt Injection | `docs/LLM01_PromptInjection.md` |
| LLM02 | Sensitive Information Disclosure | `docs/LLM02_SensitiveInformationDisclosure.md` |
| LLM03 | Supply Chain | `docs/LLM03_SupplyChain.md` |
| LLM04 | Data and Model Poisoning | `docs/LLM04_DataAndModelPoisoning.md` |
| LLM05 | Improper Output Handling | `docs/LLM05_ImproperOutputHandling.md` |
| LLM06 | Excessive Agency | `docs/LLM06_ExcessiveAgency.md` |
| LLM07 | System Prompt Leakage | `docs/LLM07_SystemPromptLeakage.md` |
| LLM08 | Vector and Embedding Weaknesses | `docs/LLM08_VectorAndEmbeddingWeaknesses.md` |
| LLM09 | Misinformation | `docs/LLM09_Misinformation.md` |
| LLM10 | Unbounded Consumption | `docs/LLM10_UnboundedConsumption.md` |

---

## 7. Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11+ |
| LLM API | Anthropic SDK (`anthropic>=0.40.0`) |
| Build system | Hatchling (pyproject.toml) |
| Default model | `claude-sonnet-4-20250514` |
| Output format | Markdown |

---

## 8. Usage

```bash
# Audit a codebase directory
python -m owasp_llm_audit /path/to/agent/codebase

# Audit with output to file
python -m owasp_llm_audit /path/to/agent -o report.md

# Audit from piped input
cat architecture.md | python -m owasp_llm_audit -

# Dry run (no API call, sample report)
python -m owasp_llm_audit /path/to/agent --dry-run

# Specify model
python -m owasp_llm_audit /path/to/agent -m claude-opus-4-20250514
```

---

## 9. Roadmap / Open Work

| Priority | Item | Type | Description |
|----------|------|------|-------------|
| P0 | Tests | Skill | Add unit tests for collector, controls, auditor, and report modules |
| P0 | CI pipeline | Workflow | GitHub Actions for lint, test, and dry-run on PRs |
| P1 | Parallel control assessment | Agent | Assess controls concurrently to reduce wall-clock audit time |
| P1 | Structured output validation | Skill | JSON schema validation for auditor responses instead of loose parsing |
| P2 | Custom control definitions | Skill | Allow users to add org-specific controls beyond the OWASP Top 10 |
| P2 | Diff-mode audit | Skill | Audit only changed files (git diff) for incremental re-assessment |
| P3 | Multi-agent comparison | Workflow | Audit multiple agents and produce a comparative scorecard |
| P3 | Evidence attachments | Skill | Attach code snippets and config excerpts as evidence to each finding |

---

## 10. Community Contribution

This plan is submitted to the SAAF community. Each component (skills S1–S4, agent A1, workflow W1) is designed to be independently reusable:

- **S3: control-assessor** can be composed into any agent that needs per-control LLM security assessment.
- **S1: material-collector** can be reused by any audit agent that needs to ingest codebases.
- **W1: full-audit-workflow** can serve as a template for other OWASP-based audit workflows.

Organizations can extend this by adding custom controls (P2), integrating with their CI pipelines (P0), or building comparative dashboards (P3).
