# LLM10:2025 Unbounded Consumption

## Overview

This vulnerability describes how LLM applications can be exploited through uncontrolled inference, enabling denial of service attacks, financial depletion, and model theft. The high computational demands of LLMs create targets for resource exploitation.

## Key Vulnerability Types

1. **Variable-Length Input Flood** — Overloading systems with numerous inputs of varying sizes
2. **Denial of Wallet (DoW)** — Exploiting pay-per-use pricing models to cause financial damage
3. **Continuous Input Overflow** — Exceeding context windows to drain computational resources
4. **Resource-Intensive Queries** — Submitting complex queries that consume excessive processing power
5. **Model Extraction via API** — Collecting outputs to replicate partial models through careful prompt engineering
6. **Functional Model Replication** — Using target models to generate synthetic training data for competitor models
7. **Side-Channel Attacks** — Exploiting input filtering to harvest model weights and architectural data

## Prevention and Mitigation Strategies

- Input validation and size limits
- Restricting logits/logprobs exposure
- Rate limiting and user quotas
- Dynamic resource allocation monitoring
- Timeouts and throttling mechanisms
- Sandbox restrictions on system access
- Comprehensive logging and anomaly detection
- Watermarking frameworks
- Graceful system degradation
- Access controls and MLOps governance
- Budget alerts and spending caps for API usage
- Token counting and request size validation
- Queue management for high-load scenarios

## Example Attack Scenarios

- Attacker sends thousands of varied-length requests to exhaust compute resources
- Malicious user exploits pay-per-token API to run up costs (Denial of Wallet)
- Competitor systematically queries API to extract and replicate the model
- Side-channel analysis of response timing reveals model architecture details

## Related Standards

- MITRE CWE (Common Weakness Enumeration)
- MITRE ATLAS (Adversarial Threat Landscape for AI Systems)
- OWASP resource consumption frameworks
