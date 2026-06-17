# LLM08 — Vector and Embedding Weaknesses

## Description
Vector and Embedding Weaknesses arise in RAG (Retrieval-Augmented Generation) and embedding-based systems. Attackers can manipulate the vector store, poison embeddings, or exploit retrieval logic to influence model outputs with malicious or misleading content.

## Risk
- Malicious documents inserted into the vector store influence retrieved context
- Embedding similarity attacks retrieve attacker-controlled content for specific queries
- Data leakage via cross-user retrieval in multi-tenant vector stores
- Model inversion attacks reconstruct training data from embeddings

## Key Assessment Questions
1. Is write access to the vector store/RAG knowledge base access-controlled?
2. Are documents validated and scanned before ingestion into the vector store?
3. Is there tenant isolation in multi-user RAG deployments?
4. Are retrieval results validated before being included in the model context?
5. Is the embedding model itself from a trusted, verified source?

## Mitigations
- Restrict write access to the vector store to authorised processes only
- Validate and hash all documents before ingestion
- Implement tenant isolation with namespace separation in multi-tenant deployments
- Monitor retrieved chunks for anomalous content before including in context
- Version-control the vector store and support rollback
