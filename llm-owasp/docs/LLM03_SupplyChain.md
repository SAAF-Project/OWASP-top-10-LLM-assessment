# LLM03:2025 Supply Chain

## Overview

Vulnerabilities in LLM supply chains can compromise training data, models, and deployment platforms, potentially resulting in biased outputs, security breaches, or system failures.

## Key Risk Categories

1. **Traditional Third-party Package Vulnerabilities** — Outdated or deprecated components exploitable by attackers, similar to OWASP A06:2021.
2. **Licensing Risks** — Diverse software and dataset licenses creating legal compliance challenges if mismanaged across open-source and proprietary contexts.
3. **Outdated or Deprecated Models** — Unmaintained models introducing security vulnerabilities.
4. **Vulnerable Pre-Trained Models** — Models are binary black boxes with potential hidden biases, backdoors, or malicious features undetectable through standard safety evaluations.
5. **Weak Model Provenance** — Insufficient assurances regarding model origins, enabling account compromises and social engineering attacks.
6. **Vulnerable LoRA Adapters** — Malicious fine-tuning components compromising base model integrity.
7. **Exploitable Collaborative Development** — Model merge services exploitable to introduce vulnerabilities bypassing security reviews.
8. **On-Device LLM Vulnerabilities** — Increased attack surface from compromised manufacturing and firmware exploitation.
9. **Unclear Terms and Privacy Policies** — Sensitive data exposure through model training and copyright violations.

## Prevention and Mitigation Strategies

- Vet data sources and suppliers thoroughly with regular security audits
- Apply OWASP A06:2021 component management controls
- Conduct comprehensive AI red teaming before model selection
- Maintain Software Bills of Materials (SBOMs) for component tracking
- Create licensing inventories with automated compliance monitoring
- Use models from verifiable sources with integrity verification
- Implement monitoring for collaborative development environments
- Deploy anomaly detection and adversarial robustness testing
- Establish patching policies for vulnerable components
- Encrypt edge-deployed models with integrity checks

## Example Attack Scenarios

- Compromised Python library exploits (PyTorch, Ray framework)
- Direct model parameter tampering (PoisonGPT)
- Safety feature removal through fine-tuning with benchmark evasion
- Malicious LoRA adapter injection
- Cloud infrastructure attacks (CloudBorne, CloudJacking)
- GPU memory exploitation (CVE-2023-4969)
- Mobile application reverse-engineering and model replacement
- Dataset poisoning creating hidden backdoors
- Privacy policy manipulation enabling unauthorized data use
