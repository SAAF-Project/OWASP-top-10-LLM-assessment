# LLM05:2025 Improper Output Handling

## Core Issue

This vulnerability involves inadequate validation and sanitization of LLM-generated outputs before downstream processing. LLM-generated content can be controlled by prompt input, creating indirect system access risks.

## Key Risks

Exploitation can enable XSS, CSRF, SSRF, privilege escalation, and remote code execution. Aggravating factors include:
- Excessive LLM system privileges
- Indirect prompt injection susceptibility
- Weak third-party input validation
- Missing context-specific encoding
- Poor monitoring practices
- Absent rate limiting

## Primary Vulnerability Types

1. **Direct shell execution** of LLM responses
2. **Browser interpretation** of malicious JavaScript/Markdown
3. **Unparameterized SQL query execution**
4. **Path traversal** via unsanitized file paths
5. **Phishing** via unescaped email templates
6. **Compromised code generation** and dependency risks

## Prevention and Mitigation Strategies

- Treat LLM outputs with a **zero-trust approach**
- Implement OWASP ASVS (Application Security Verification Standard) controls
- Apply context-aware output encoding
- Use parameterized queries for all database interactions
- Implement Content Security Policies (CSP)
- Deploy robust logging systems for anomaly detection
- Validate and sanitize all LLM outputs before passing to downstream systems
- Never directly execute LLM-generated code without sandboxing
- Implement output format validation against expected schemas

## Example Attack Scenarios

- LLM generates SQL that gets executed without parameterization
- LLM output containing JavaScript rendered in a web UI causes XSS
- LLM-generated file paths used to access unauthorized filesystem locations
- LLM crafts email content that enables phishing attacks
