# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

Three AI-powered tools sharing the same repo:

1. **Audit Document Reviewer** (`review_document.py`) — reviews internal audit documents (control descriptions, process docs, policies) and returns structured findings, gaps, risks, and recommendations.
2. **OWASP LLM Agent Reviewer** (`review_agent.py` + `app.py`) — reviews agent source code and configs against the OWASP Top 10 for LLM Applications (2025 edition). Available as both a CLI and a Flask web portal.
3. **SAAF Compliance Agent** (`saaf/` package) — a structured compliance report generator. Given company profile inputs, deterministically maps applicable frameworks and regulations, then calls Claude to produce a fully validated Pydantic `ComplianceReport` as JSON.

## How to run

Set the API key first:
```
set ANTHROPIC_API_KEY=sk-ant-...your-key...
```

**Audit Document Reviewer:**
```
python review_document.py my_document.txt          # single file (.txt, .docx, .pdf)
python review_document.py --folder my_folder       # all supported docs in a folder
python review_document.py                          # paste text (Ctrl+Z then Enter on Windows)
```

**OWASP Agent Reviewer (CLI):**
```
python review_agent.py my_agent.py                 # single file
python review_agent.py --folder agents_folder      # all agent files in a folder
python review_agent.py                             # paste code
```

**OWASP Agent Reviewer (Web Portal):**
```
pip install flask
python app.py                                      # opens http://localhost:5000
```

## Dependencies

```
pip install anthropic python-docx pypdf flask pydantic rich
```

## Architecture

**`review_document.py`** — self-contained. Supports `.txt`, `.docx`, `.pdf`. Two-call pattern per document: streaming `review_document()` call produces the structured audit review, then a non-streaming `assess_risk()` call assigns High/Medium/Low. In folder mode, `save_priority_report()` writes `priority_report.txt` sorted by risk into `<folder>/reports/`.

**`review_agent.py`** — self-contained CLI. Supports `.py`, `.js`, `.ts`, `.json`, `.yaml`, `.yml`, `.txt`, `.md`. Same two-call pattern: streaming `review_agent()` produces OWASP per-category findings, then `assess_risk()` extracts Critical/High/Medium/Low. In folder mode, writes `<filename>_owasp_review.txt` files and `owasp_priority_report.txt` into `<folder>/reports/`. Uses `thinking: {"type": "adaptive"}` on the main review call. Exports `SYSTEM_PROMPT` and `SUPPORTED_EXTENSIONS` for use by `app.py`.

**`app.py`** — Flask web portal. Imports `SYSTEM_PROMPT` and `SUPPORTED_EXTENSIONS` from `review_agent`. The single `/review` POST route streams Claude's response directly to the browser using `stream_with_context`. All HTML/CSS/JS is inlined as a string constant. Port defaults to `5000`, overridable via `PORT` env var.

**`saaf/` package** — structured compliance agent, in-development. Pipeline:
1. `FrameworkMapper` (`core/mapper.py`) — pure-Python, no API call. Resolves jurisdiction from country string, then walks `FRAMEWORK_REGISTRY` (`knowledge/frameworks.py`) and `REGULATORY_MATRIX` (`knowledge/regulations.py`) to determine applicable frameworks (capped at 8) and mandatory regulations.
2. `build_system_prompt` / `build_user_message` (`prompts/system_prompt.py`) — assembles prompts dynamically from the mapper output; injects only the relevant framework knowledge.
3. `ComplianceAgent.run()` (`core/agent.py`) — calls Claude with streaming + `thinking: {"type": "adaptive"}`, retries once on 5xx errors, extracts the JSON text block, strips markdown fences, then validates against the `ComplianceReport` Pydantic schema (`core/models.py`).
4. `output/formatter.py` — Rich-based CLI renderer for the final report.

`ComplianceAgent` reads settings from a `Config` class (expected at `config.py` in the repo root — **not yet committed**).

**`project_2026-03-24/`** — standalone prototype folder: a simpler Flask app (`app.py`) using a Jinja2 template (`templates/index.html`) instead of inlined HTML, plus `test_agent.py` (intentionally insecure sample agent for testing the OWASP reviewer).

**Model used:** `claude-opus-4-6` for all API calls across all tools.
