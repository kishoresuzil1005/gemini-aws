# ADR-004: In-Process Memory Store for Conversation Context

| Field | Value |
|-------|-------|
| Date | 2026-06-25 |
| Status | Accepted |
| Deciders | Kishore Suzil |
| Supersedes | — |

## Context

The GraphAssistant needs to maintain **per-conversation context** — the current resource being discussed, recent message history, and intent state — across multiple turns of a conversation. A decision must be made on where and how to store this state.

## Decision

Use an **in-process Python dictionary** (`MemoryStore`) as the conversation memory backend. Each conversation is keyed by `conversation_id`. Context and message history are stored in `_context` and `_history` dictionaries, respectively. The `MemoryManager` provides a higher-level API over `MemoryStore`.

## Rationale

- Zero infrastructure overhead — no Redis, database, or external service needed.
- Simplifies the development and deployment story for v1.
- Sufficient for single-instance deployments (which is the current architecture: one backend container).
- Conversation sessions are short-lived (minutes to hours); durability is not required.

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| Redis | Adds infrastructure dependency; overkill for single-instance deployment. |
| PostgreSQL session table | SQL round-trips on every message turn add latency. |
| File system | Slow, not thread-safe without locking, hard to purge stale sessions. |

## Consequences

### Positive
- Zero latency for memory reads/writes.
- No external dependency.
- Simple to debug and inspect.

### Negative
- Memory is **lost on process restart** — all conversation context is ephemeral.
- Does **not scale horizontally** — if multiple backend instances are running, each has its own memory store (sessions are not shared).
- No automatic expiration — long-running processes could accumulate stale sessions (future: add TTL-based eviction).

## Future Migration Path

When horizontal scaling is required, replace `MemoryStore` with a Redis-backed implementation behind the same `MemoryStore` interface. No changes to `MemoryManager` or higher-level callers will be needed.

## References

- [MemoryStore](../../app/services/ai/assistant/memory/memory_store.py)
- [MemoryManager](../../app/services/ai/assistant/memory/memory_manager.py)
- [GraphAssistant](../../app/services/ai/assistant/graph_assistant.py)
