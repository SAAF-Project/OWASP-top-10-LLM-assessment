# LLM07:2025 System Prompt Leakage

## Core Vulnerability

System prompt leakage involves exposure of instructions designed to guide LLM behavior. Critically, **the system prompt should not be considered a secret, nor should it be used as a security control.** The actual risk stems from underlying security weaknesses rather than prompt disclosure itself.

## Primary Risk Categories

- **Sensitive Data Exposure** — System prompts may contain API keys, database credentials, or authentication tokens that attackers can extract for unauthorized access.
- **Internal Rules Disclosure** — Operational parameters (transaction limits, loan amounts) become visible, enabling attackers to circumvent established controls.
- **Filtering Mechanism Revelation** — Content moderation rules become apparent, allowing attackers to craft bypasses.
- **Permission Structure Exposure** — Role-based access information can facilitate privilege escalation attempts.

## Prevention and Mitigation Strategies

1. **Externalize Sensitive Data** — Keep credentials and permission structures outside prompt language entirely.
2. **Avoid Prompt-Based Controls** — Implement critical security functions in external systems rather than relying on LLM adherence to instructions.
3. **Deploy Independent Guardrails** — Use output inspection systems separate from the LLM to enforce compliance expectations.
4. **Enforce Controls Externally** — Security functions like authorization must operate deterministically outside the LLM through proper system architecture.

## Key Insight

Disclosure of the system prompt itself does not present the real risk — the security risk lies with the underlying elements. Never store secrets in system prompts, and never rely on prompt instructions as a security boundary.
