# ADR-002: Use Ollama as the Local LLM Provider

| Field | Value |
|-------|-------|
| Date | 2026-06-25 |
| Status | Accepted |
| Deciders | Kishore Suzil |
| Supersedes | — |

## Context

CloudOps AI requires a large-language model for chat, recommendation generation, and architecture analysis. The platform is deployed in a private AWS environment where sending data to external LLM APIs (OpenAI, Anthropic, etc.) raises **data privacy and cost concerns**. A self-hosted solution is preferred.

## Decision

Use **Ollama** as the local LLM server. The platform calls the Ollama REST API (`/api/chat`) via `OllamaProvider`. The model (`mistral` or any supported model) runs in the same network as the backend container.

## Rationale

- Runs entirely on-premises — no data leaves the private network.
- Zero per-token cost after hardware provisioning.
- Supports model swapping without code changes (model name is configurable via `OLLAMA_MODEL` env var).
- Simple HTTP API compatible with the abstracted `BaseProvider` interface.
- Supports streaming responses (`stream=True`).

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| OpenAI API | Data privacy risk; ongoing per-token cost; requires internet access. |
| AWS Bedrock | Requires internet/VPC endpoint; adds cloud coupling and cost. |
| HuggingFace Inference | More complex setup; not as operationally simple as Ollama. |
| vLLM | More appropriate for high-throughput production; overkill for current scale. |

## Consequences

### Positive
- Full data privacy.
- No ongoing API costs.
- Pluggable via `BaseProvider` abstraction — easy to swap in a future provider.
- Health checks, retry logic, and circuit breaker implemented in `OllamaProvider`.

### Negative
- Response quality depends on the locally hosted model.
- Requires GPU-capable EC2 instance for good performance.
- Cold-start latency if the model is not pre-loaded.
- Model updates require manual action (not automatic).

## References

- [OllamaProvider](../../app/services/ai/assistant/llm/ollama_provider.py)
- [BaseProvider](../../app/services/ai/assistant/llm/base_provider.py)
- [Ollama Documentation](https://ollama.ai/docs)
