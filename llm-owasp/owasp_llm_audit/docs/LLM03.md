# LLM03 — Supply Chain

## Description
LLM supply chain vulnerabilities arise from compromised or tampered components: pre-trained models, fine-tuning datasets, plugins, third-party integrations, or dependencies. A malicious component can backdoor the entire agent pipeline.

## Risk
- Compromised base model with embedded backdoors
- Malicious third-party plugins executing arbitrary code
- Tampered training/fine-tuning datasets introducing biases or trojans
- Vulnerable dependencies (packages, APIs) exploited at runtime

## Key Assessment Questions
1. Are model providers verified and their integrity checksums validated?
2. Are third-party plugins or tools reviewed before integration?
3. Is the dependency graph pinned and scanned for known CVEs?
4. Is there a software bill of materials (SBOM) for the agent stack?
5. Are fine-tuning datasets from trusted, audited sources?

## Mitigations
- Pin model versions and verify checksums before deployment
- Vet all third-party plugins; prefer audited, well-maintained ones
- Scan dependencies with a CVE scanner (e.g., pip-audit, Safety)
- Maintain an SBOM and review it on each release
- Restrict network access for model inference where possible
