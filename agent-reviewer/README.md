# OWASP LLM Agent Reviewer

Reviews agent source code and configs against the **OWASP Top 10 for LLM Applications (2025)**.
Available as both a CLI tool and a Flask web portal.

## Setup

```bash
pip install anthropic flask
export ANTHROPIC_API_KEY=sk-ant-...
```

## CLI usage

```bash
# Single file
python review_agent.py my_agent.py

# Multiple files (multi-agent system)
python review_agent.py agent1.py agent2.py agent3.py

# All files in a folder (generates per-file reports + priority report)
python review_agent.py --folder agents_folder

# Show extended thinking
python review_agent.py --thinking my_agent.py

# Update OWASP definitions from URL
python review_agent.py --update-owasp
python review_agent.py --update-owasp https://example.com/owasp_llm_top10.json
```

## Web portal

```bash
python app.py        # opens http://localhost:5000
```

Features: file upload, drag-and-drop, multi-agent cards, extended thinking panel,
audit bar (timestamp + SHA-256 hashes), copy/download report as `.md`.

## OWASP definitions

Categories are loaded from `owasp_llm_top10.json` — edit this file or run
`--update-owasp` to pull a fresh copy. The web portal badge turns amber after
30 days and links to the OWASP changelog.

## Output

Each review covers LLM01–LLM10 with Status / Evidence / Findings / Recommendation
per category, plus an Overall Compliance Summary (Critical / High / Medium / Low).
Reports include a SHA-256 audit header for reperformance traceability.
