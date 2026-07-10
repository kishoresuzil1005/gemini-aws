# ADR-003: Use Qdrant + nomic-embed-text for RAG

| Field | Value |
|-------|-------|
| Date | 2026-06-25 |
| Status | Accepted |
| Deciders | Kishore Suzil |
| Supersedes | — |

## Context

The CloudOps AI assistant needs to answer questions grounded in AWS documentation and cloud best practices. Without a retrieval layer, the LLM either hallucinates or lacks domain-specific knowledge. A Retrieval-Augmented Generation (RAG) approach — indexing documentation into a vector store and retrieving relevant chunks at query time — solves this problem without fine-tuning.

## Decision

Use **Qdrant** as the vector database and **nomic-embed-text** (via Ollama) as the embedding model. Documents are chunked, embedded, and upserted into Qdrant. At query time, the user's message is embedded and used to retrieve the top-K most similar chunks, which are injected into the LLM prompt as context.

## Rationale

- Qdrant is open-source, self-hosted, and provides a simple REST API.
- nomic-embed-text is a high-quality open-source embedding model available locally via Ollama — no external API needed.
- The `RAGService` + `QdrantService` + `EmbeddingService` stack is modular and can swap the vector database or embedding model independently.
- Retrieval optimization via `RetrievalOptimizer` (min-score filtering, category mapping) improves answer quality.

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| pgvector (PostgreSQL extension) | Slower for large collections; limited ANN algorithms. |
| Pinecone / Weaviate Cloud | External SaaS; data privacy concerns; ongoing cost. |
| FAISS (in-process) | Not persistent across restarts; no REST API; harder to manage. |
| OpenAI text-embedding-ada | External API; cost and privacy concerns. |

## Consequences

### Positive
- Fully self-hosted; no data leaves the environment.
- Modular design: embedding model and vector store are independently swappable.
- Collection-per-domain approach allows targeted retrieval (e.g., `cloud_docs` vs. `security_docs`).

### Negative
- Requires running a Qdrant container alongside the backend.
- Index quality depends on chunk size, overlap, and embedding model.
- No built-in re-ranking; semantic similarity alone may surface irrelevant chunks.

## References

- [RAGService](../../app/services/ai/rag_service.py)
- [QdrantService](../../app/services/ai/qdrant_service.py)
- [EmbeddingService](../../app/services/ai/embedding_service.py)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
