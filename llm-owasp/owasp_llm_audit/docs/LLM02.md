# LLM02 — Sensitive Information Disclosure

## Description
LLMs may inadvertently reveal confidential data, proprietary algorithms, or personal information through their responses. This occurs when the model has been trained on, or given access to, sensitive data and fails to restrict its output appropriately.

## Risk
- PII, credentials, API keys exposed in model outputs
- Confidential business logic or system architecture leaked
- Training data memorisation leads to disclosure of private records
- Regulatory violations (GDPR, CCPA) from uncontrolled PII output

## Key Assessment Questions
1. Are credentials, API keys, or secrets ever included in prompts or context?
2. Does the agent have access to personal data? If so, is output filtered before delivery?
3. Is the system prompt visible to users, and does it contain sensitive configuration?
4. Are there output validation controls that redact PII before returning results?
5. Is data minimisation applied — does the agent only receive data it needs?

## Mitigations
- Never include credentials or secrets in prompts; use environment variables
- Apply output filtering to redact PII patterns (email, SSN, card numbers)
- Limit context window to minimum necessary data
- Audit all data sent to the model API
- Use structured output schemas to prevent free-text data leakage
