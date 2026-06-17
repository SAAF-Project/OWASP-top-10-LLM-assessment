# LLM06 — Excessive Agency

## Description
Excessive Agency occurs when an LLM agent is granted more permissions, capabilities, or autonomy than required for its task. When combined with prompt injection or model errors, this can result in unintended destructive or unauthorised actions.

## Risk
- Agent deletes or modifies files/records beyond its intended scope
- Agent sends emails, makes API calls, or executes actions without human approval
- Compromised or hallucinating agent causes irreversible damage
- Privilege escalation via tool chaining

## Key Assessment Questions
1. Does the agent operate on the principle of least privilege?
2. Are destructive or irreversible actions gated behind human-in-the-loop checkpoints?
3. Is the tool set constrained to only what is needed for the specific task?
4. Are there rate limits or action budgets on tool calls?
5. Can the agent be stopped or rolled back mid-execution?

## Mitigations
- Apply least-privilege: grant only the minimum tools and permissions needed
- Require human approval for irreversible actions (file deletion, email, payments)
- Implement action budgets and rate limiting on tool calls
- Log all tool invocations with full audit trail
- Design for reversibility: prefer draft/preview over direct execution
