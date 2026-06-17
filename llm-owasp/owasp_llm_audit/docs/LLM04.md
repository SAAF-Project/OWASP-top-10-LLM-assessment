# LLM04 — Data and Model Poisoning

## Description
Data poisoning occurs when training, fine-tuning, or RAG corpus data is manipulated to introduce vulnerabilities, backdoors, or biases. Model poisoning targets the model weights directly. Both can cause the model to behave maliciously or incorrectly in production.

## Risk
- Backdoored model activates on trigger phrases
- Biased outputs due to tampered training data
- RAG retrieval returns attacker-controlled content
- Model produces incorrect advice in safety-critical audit contexts

## Key Assessment Questions
1. Is the training and fine-tuning data sourced from verified, controlled repositories?
2. Is the RAG knowledge base content curated and access-controlled?
3. Are there integrity checks on data ingested into the vector store?
4. Is the model re-evaluated after each fine-tuning run for behavioural drift?
5. Are there anomaly detection mechanisms on model outputs in production?

## Mitigations
- Validate and sign all training datasets; maintain provenance records
- Apply access controls and integrity hashing to RAG corpus
- Use model evaluation benchmarks after every fine-tuning run
- Monitor production outputs for statistical anomalies
- Separate write and read paths for the knowledge base
