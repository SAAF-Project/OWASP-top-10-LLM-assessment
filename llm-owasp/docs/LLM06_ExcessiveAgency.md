# LLM06:2025 Excessive Agency

## Core Vulnerability

Excessive Agency occurs when LLM-based systems perform damaging actions due to unexpected or manipulated outputs. The issue stems from three root causes: excessive functionality, excessive permissions, or excessive autonomy granted to LLM agents.

## Key Risk Categories

- **Functional Overreach** — Systems may include unneeded capabilities. For example, an extension intended to read data connects to a database server using an identity that not only has SELECT permissions, but also UPDATE, INSERT and DELETE permissions.
- **Leftover Development Tools** — Deprecated plugins sometimes remain accessible to agents after being replaced.
- **Inadequate Input Filtering** — Extensions may fail to restrict commands to their intended scope.
- **Overprivileged Access** — Agents connect with higher permissions than necessary for their purpose.
- **Generic Identities** — Shared high-privilege accounts bypass user-specific access controls.
- **Insufficient Verification** — Systems execute high-impact actions without human confirmation.

## Prevention and Mitigation Strategies

- **Minimize scope** across three dimensions: limit available extensions, restrict extension functions, and reduce granted permissions
- Use granular tools instead of broad ones like shell commands or URL fetchers
- Implement user context authentication via OAuth with minimal scopes
- Require human approval for significant actions
- Enforce authorization in downstream systems rather than relying on LLM decision-making
- Implement activity logging and monitoring
- Apply rate-limiting to reduce damage scope when vulnerabilities exist

## Example Attack Scenarios

- A mail summarization app vulnerable to indirect prompt injection could send sensitive information to attackers if granted unnecessary sending capabilities and without user review steps
- An agent with file system write access is tricked into overwriting critical system files
- A database-connected agent with excessive permissions deletes records due to prompt manipulation
