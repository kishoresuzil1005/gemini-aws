# Review Metadata Header

Add this block at the very top of **every** subsystem architecture review document, immediately below the document title (H1).

```markdown
| Field | Value |
|-------|-------|
| Review Version | 1.0 |
| Review Date | YYYY-MM-DD |
| Reviewer | <Your Name> |
| Subsystem Version | v1.x *(optional – use if the subsystem has its own version tag)* |
| Status | Draft / Approved |
| Code Version | `<git rev-parse --short HEAD>` |
```

## Field Definitions

| Field | Description |
|-------|-------------|
| **Review Version** | Version of the Architecture Review Template used. Frozen at 1.0. |
| **Review Date** | ISO‑8601 date when the review was completed (`YYYY-MM-DD`). |
| **Reviewer** | Name(s) of the engineer(s) who wrote the review. |
| **Subsystem Version** | Optional. Use if the subsystem has its own semantic version separate from the project release. |
| **Status** | `Draft` – in progress. `Approved` – signed off by tech lead. |
| **Code Version** | Short git commit SHA that the review was based on. Run `git rev-parse --short HEAD` to get it. |

## Example (Filled In)

| Field | Value |
|-------|-------|
| Review Version | 1.0 |
| Review Date | 2026-07-10 |
| Reviewer | Kishore Suzil |
| Subsystem Version | v2.1 |
| Status | Approved |
| Code Version | `13d1019` |

---

*CloudOps AI Architecture Standards — Review Metadata Header v1.0*
