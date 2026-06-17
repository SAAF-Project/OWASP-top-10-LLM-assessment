"""Claude Code integration — slash command and subagent entry points."""

from pathlib import Path

from owasp_llm_audit.auditor import run_audit


def slash_audit(target: str = ".", output: str | None = None, model: str = "claude-sonnet-4-20250514") -> str:
    """Entry point for /audit slash command in Claude Code.

    Usage from Claude Code:
        /audit                  — audit current directory
        /audit path/to/agent    — audit a specific path
        /audit -o report.md     — write report to file

    Args:
        target: Path or description to audit. Defaults to current directory.
        output: Optional file path to write the report.
        model: Claude model to use.

    Returns:
        The formatted markdown audit report.
    """
    return run_audit(target, model=model, output_path=output)


def subagent_audit(target: str, model: str = "claude-sonnet-4-20250514") -> str:
    """Entry point for programmatic use by other Claude Code agents.

    Example:
        from owasp_llm_audit.claude_code import subagent_audit
        report = subagent_audit("/path/to/agent/project")

    Args:
        target: Path or description to audit.
        model: Claude model to use.

    Returns:
        The formatted markdown audit report.
    """
    return run_audit(target, model=model)
