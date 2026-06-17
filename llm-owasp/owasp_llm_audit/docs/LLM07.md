# LLM07 — System Prompt Leakage

## Description
System Prompt Leakage occurs when an LLM reveals its system prompt or internal instructions to users. This exposes proprietary business logic, security configurations, and can aid attackers in crafting targeted injection attacks.

## Risk
- Proprietary prompt engineering logic exposed to competitors or attackers
- Security-by-obscurity controls defeated once system prompt is known
- Attackers use system prompt knowledge to craft targeted bypass attacks
- Confidential business rules or data handling instructions leaked

## Key Assessment Questions
1. Is the system prompt designed to be kept confidential?
2. Does the system prompt contain sensitive information that must not be disclosed?
3. Are there explicit instructions in the system prompt about confidentiality?
4. Has the agent been tested to verify it does not reveal the system prompt on request?
5. Are there output filters that detect and block system prompt disclosure?

## Mitigations
- Do not include credentials or truly sensitive data in system prompts
- Instruct the model explicitly not to reveal or summarise its system prompt
- Test regularly: attempt to extract system prompt via social engineering prompts
- Use API-level system prompt confidentiality features where available
- Design security controls not to rely solely on system prompt secrecy
