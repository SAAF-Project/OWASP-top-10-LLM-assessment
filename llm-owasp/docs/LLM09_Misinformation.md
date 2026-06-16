# LLM09:2025 Misinformation

## Core Vulnerability

LLMs generate false or misleading information that appears credible, causing security breaches, reputational harm, and legal liability. The primary cause is hallucination — fabricated content that sounds accurate but lacks factual basis.

## Key Risk Categories

- **Factual Inaccuracies** — Models produce incorrect statements. Air Canada's chatbot provided false traveler information, resulting in operational disruption and successful litigation.
- **Unsupported Claims** — Baseless assertions appear in sensitive domains. ChatGPT invented fake legal cases, causing courtroom complications.
- **Misrepresentation of Expertise** — Systems suggest false confidence levels on complex topics, misleading users about treatment validity and medical certainty.
- **Unsafe Code Generation** — Models recommend nonexistent or insecure libraries, introducing vulnerabilities when developers trust suggestions without verification.

## Prevention and Mitigation Strategies

1. **Retrieval-Augmented Generation** — Retrieve verified information from trusted sources
2. **Model Fine-Tuning** — Improve output quality through parameter-efficient techniques
3. **Cross-Verification and Human Oversight** — Ensure independent fact-checking
4. **Automatic Validation Mechanisms** — Validate critical outputs programmatically
5. **Risk Communication** — Clearly disclose limitations to users
6. **Secure Coding Practices** — Prevent vulnerability integration from generated code
7. **User Interface Design** — Encourage responsible usage through content filters and clarity
8. **Training and Education** — Develop user critical thinking and verification skills

## Example Attack Scenarios

- Attackers identify hallucinated package names from coding assistants, publish malicious packages using those names, and compromise developer systems through unknowing integration
- Companies deploying unreliable medical chatbots face litigation without requiring active attackers — insufficient oversight alone creates liability exposure
