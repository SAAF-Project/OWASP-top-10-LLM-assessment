"""OWASP LLM Top 10 Audit Agent — checks AI agents against OWASP LLM controls."""

from owasp_llm_audit.auditor import run_audit

__all__ = ["run_audit"]
