# ADR Guidelines

> Architectural Decision Records (ADRs) are short documents that capture an important architectural decision made during the project, including the context and consequences.

---

## When to Write an ADR

Write an ADR any time a decision:

- Has significant long-term impact on the architecture.
- Involves a trade-off between alternatives.
- Was debated and is not self-evident from the code.
- Could be questioned by a future engineer.

## ADR File Naming

```
ADR-NNN-Short-Title.md
```

Examples:
- `ADR-001-Neo4j.md`
- `ADR-002-Ollama.md`
- `ADR-003-RAG-Strategy.md`

## ADR Template

```markdown
# ADR-NNN: [Short Title]

| Field | Value |
|-------|-------|
| Date | YYYY-MM-DD |
| Status | Proposed / Accepted / Deprecated / Superseded |
| Deciders | Name(s) |
| Supersedes | ADR-XXX (if applicable) |

## Context

Describe the situation and forces at play. Why was a decision needed?

## Decision

State the decision clearly. What was chosen?

## Rationale

Why was this decision made? What factors drove the choice?

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| Option A | Reason |
| Option B | Reason |

## Consequences

### Positive
- Benefit 1.
- Benefit 2.

### Negative
- Trade-off 1.
- Trade-off 2.

## References

- Link to relevant documentation, benchmarks, or prior art.
```

---

## ADR Status Lifecycle

```
Proposed → Accepted → (Deprecated | Superseded)
```

| Status | Meaning |
|--------|---------|
| Proposed | Draft, under discussion. |
| Accepted | Agreed upon and in effect. |
| Deprecated | No longer applies; left for historical reference. |
| Superseded | Replaced by a newer ADR (reference the new one). |

---

*CloudOps AI Architecture Standards — ADR Guidelines v1.0*
