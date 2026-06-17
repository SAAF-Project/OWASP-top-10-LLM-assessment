# LLM01:2025 Prompt Injection

## Core Concept

A Prompt Injection Vulnerability occurs when user prompts alter the LLM's behavior or output in unintended ways. These attacks don't require human-readable content, operating through model-parseable inputs that can bypass safety measures.

## Two Primary Attack Types

**Direct Injections** involve users deliberately or accidentally crafting prompts that alter model behavior through direct input.

**Indirect Injections** exploit external sources like websites or files that contain content capable of manipulating the model when processed.

## Potential Impacts

Successful attacks may result in:
- Sensitive information disclosure
- System infrastructure exposure
- Biased outputs
- Unauthorized function access
- Arbitrary command execution
- Compromised decision-making processes

## Prevention and Mitigation Strategies

1. **Constrain behavior** through specific role definitions in system prompts
2. **Define and validate expected output formats** using deterministic validation
3. **Implement input/output filtering** with semantic and string-checking approaches
4. **Enforce privilege control** and least privilege access principles
5. **Require human approval** for high-risk operations
6. **Segregate and clearly identify** untrusted external content
7. **Conduct regular adversarial testing** and breach simulations

## Example Attack Scenarios

- Direct injections targeting support chatbots
- Indirect injections hidden in webpages
- Unintentional triggers
- RAG system manipulation
- Code injection exploits
- Payload splitting across documents
- Multimodal prompt embedding
- Adversarial suffixes
- Multilingual obfuscation techniques

## Key Insight

Given the stochastic influence at the heart of the way models work, foolproof prevention may be impossible, requiring layered defensive approaches instead.
