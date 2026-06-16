# LLM08:2025 Vector and Embedding Weaknesses

## Overview

This vulnerability addresses risks in systems using Retrieval Augmented Generation (RAG) with Large Language Models. Weaknesses in vector and embedding processes can enable content injection, output manipulation, or sensitive data exposure.

## Primary Risk Categories

- **Unauthorized Access & Data Leakage** — Inadequate access controls permit retrieval of sensitive embeddings, potentially disclosing personal data, proprietary information, or copyrighted material without compliance.
- **Cross-Context Information Leaks** — Multi-tenant environments face context leakage risks between users sharing vector databases. New retrieved data may conflict with information learned during model training.
- **Embedding Inversion Attacks** — Attackers can exploit vulnerabilities to reverse-engineer embeddings and recover significant amounts of source information, compromising data confidentiality.
- **Data Poisoning** — Both malicious actors and unintentional sources (insiders, prompts, unverified providers) can introduce poisoned data that manipulates model outputs.
- **Behavior Alteration** — RAG augmentation can unintentionally reduce qualities like empathy while improving factual accuracy, potentially diminishing model effectiveness in certain applications.

## Prevention and Mitigation Strategies

- Implement fine-grained access controls with strict logical partitioning in vector stores
- Validate data sources thoroughly and audit knowledge base integrity regularly
- Review combined datasets from multiple sources and apply appropriate classification tags
- Maintain detailed immutable logs of retrieval activities for suspicious behavior detection
- Apply encryption to embeddings at rest and in transit
- Implement tenant isolation in multi-tenant vector database environments
- Regularly test for embedding inversion vulnerabilities

## Example Attack Scenarios

- Hidden text injection in documents that manipulates RAG retrieval
- Unauthorized cross-tenant data access in shared vector databases
- Empathy reduction through poorly curated augmentation data
