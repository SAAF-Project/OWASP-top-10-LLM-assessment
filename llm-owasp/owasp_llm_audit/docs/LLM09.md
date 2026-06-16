# LLM09 — Misinformation

## Description
LLMs can generate plausible-sounding but incorrect information (hallucinations). In audit and compliance contexts, misinformation can lead to incorrect risk assessments, missed controls, or erroneous regulatory conclusions.

## Risk
- Auditors rely on hallucinated findings as factual evidence
- Incorrect regulatory citations in compliance reports
- False assurance: agent reports PASS for a control it has not properly assessed
- Incorrect remediation advice leads to ineffective risk treatment

## Key Assessment Questions
1. Does the agent instruct the model to cite only evidence present in the provided material?
2. Are model outputs validated against source documents before use?
3. Is there a hallucination detection layer (e.g., claim verification via RAG)?
4. Are uncertainty or confidence signals surfaced to the human reviewer?
5. Does the agent require human review before findings are finalised?

## Mitigations
- Use explicit prompting: "base assessment only on evidence present in the material"
- Implement a hallucination detection layer (extract claims → RAG verify → flag unverified)
- Require human review checkpoint before any finding is treated as final
- Surface model confidence or uncertainty signals in the report
- Cross-validate findings against a second model or rule-based checks
