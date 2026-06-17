# LLM01 — Prompt Injection

## Description
Prompt Injection occurs when an attacker manipulates an LLM through crafted inputs, causing it to execute unintended actions or ignore its original instructions. This includes direct injection (via user-controlled input to the model) and indirect injection (via untrusted external content — documents, web pages, tool outputs — that the model processes).

## Risk
- Attacker bypasses safety guardrails or system prompt restrictions
- Confidential system prompt contents are exposed
- Unauthorised actions executed on behalf of the attacker
- Data exfiltrated via tool calls triggered by injected instructions

## Key Assessment Questions
1. Does the agent distinguish between trusted instructions (system prompt) and untrusted user input?
2. Is user input sanitised or escaped before being included in prompts?
3. Are tool outputs treated as untrusted and validated before use in further reasoning?
4. Does the agent use a fixed system prompt that cannot be overridden by user input?
5. Is there any privilege separation between different prompt layers?

## Mitigations
- Apply strict input validation and sanitisation
- Use separate prompt layers with clear trust boundaries
- Treat all external content (documents, API responses, tool outputs) as untrusted
- Implement output validation before executing tool calls
- Log and alert on prompt injection patterns
