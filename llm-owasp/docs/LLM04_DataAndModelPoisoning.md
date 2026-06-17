# LLM04:2025 Data and Model Poisoning

## Overview

Data and model poisoning targets the integrity of training data and fine-tuning processes to introduce vulnerabilities, backdoors, or biases into LLMs. Poisoned data can compromise model security, performance, and ethical behavior.

## Key Risk Categories

- **Training Data Manipulation** — Injecting malicious content into training datasets to alter model behavior
- **Fine-tuning Attacks** — Manipulating fine-tuning processes to introduce targeted vulnerabilities
- **Backdoor Insertion** — Planting triggers that activate malicious behavior under specific conditions
- **Bias Introduction** — Deliberately skewing training data to produce biased outputs
- **Data Integrity Compromise** — Corrupting data pipelines to degrade model quality

## Prevention and Mitigation Strategies

- Verify supply chain integrity of training data with tools like "ML-BOM" (ML Bill of Materials)
- Validate data legitimacy during training and fine-tuning stages
- Implement robust data sanitization and anomaly detection
- Use adversarial robustness techniques and federated learning
- Monitor for model drift and unexpected behavior changes
- Maintain separate environments for training and deployment
- Conduct regular audits of data sources and pipelines
- Implement cryptographic verification of training data integrity
- Apply statistical testing to detect poisoned data samples
- Use ensemble methods to reduce impact of individual model compromise

## Example Attack Scenarios

- Attackers inject subtly poisoned data into public training datasets
- Fine-tuning with compromised datasets introduces hidden backdoors
- Malicious actors manipulate data labels to create biased model outputs
- Insider threats modify training pipelines to degrade model performance
- Social engineering attacks target data annotation teams
