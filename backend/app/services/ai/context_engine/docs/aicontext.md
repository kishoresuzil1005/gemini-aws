# AIContext Reference

## Overview

`AIContext` is the canonical context object returned by `ContextEngine.build()`.
It is treated as **read-only** once assembled.

Every AI feature in the platform should consume `AIContext`, not call providers directly.

## Full Schema

```python
AIContext(
    # ── Engine-level metadata ──────────────────────────────
    metadata={
        "schema_version": "1.0",     # bump when AIContext schema changes
        "engine_version":  "1.0.0",  # bump when engine logic changes
        "generated_at":    str,       # ISO-8601 UTC timestamp
        "context_level":   str,       # "basic" | "standard" | "full" | "deep"
    },

    # ── Execution tracking ─────────────────────────────────
    execution=ExecutionMetadata(
        providers_executed=List[str],  # successfully completed providers
        providers_failed=List[str],    # failed providers (non-strict mode)
        cache_hits=int,                # number of cache hits
        start_time=datetime,
        end_time=datetime,
        duration_seconds=float,
    ),

    # ── Provider sections ──────────────────────────────────
    resource={
        "id":       str,    # resource_id (e.g. "i-0abc123")
        "name":     str,
        "type":     str,    # "EC2" | "RDS" | "S3" ...
        "provider": str,    # "aws" | "azure" | "gcp"
        "region":   str,
        "account":  str,
        "arn":      str,
        "status":   str,
        "tags":     dict,
    },

    graph={
        "resource": dict,       # root node
        "nodes":    List[dict], # all nodes in the graph
        "edges":    List[dict], # all edges
        "subgraph": {           # 1-hop neighborhood of the resource
            "nodes": List[dict],
            "edges": List[dict],
        },
    },

    inventory={
        "resource_id":     str,
        "account_id":      str,
        "organization":    str,
        "environment":     str,   # "prod" | "staging" | "dev"
        "project":         str,
        "region":          str,
        "provider":        str,
        "owner":           str,
        "tags":            dict,
        "metadata":        dict,
        "scanner_version": str,
        "last_discovered": str,   # ISO-8601
    },

    security={   # populated by IAMProvider (FULL/DEEP only)
        "identities":            List[dict],
        "permissions":           List[dict],
        "trust_relationships":   List[dict],
        "permission_boundaries": List[dict],
    },

    documentation={   # populated by DocumentationProvider (FULL/DEEP)
        "sources": [
            {
                "type":    str,    # "internal" | "qdrant" | "aws"
                "title":   str,
                "url":     str,
                "snippet": str,
                "score":   float,  # relevance 0.0–1.0
            }
        ],
        "primary_source": str,
    },

    metrics={    # populated by MetricsProvider (DEEP only)
        "look_back_hours": int,
        "period_seconds":  int,
        "datapoints": {
            "cpu_utilization":     List[{"timestamp": str, "value": float}],
            "memory_utilization":  List[...],
            "network_in":          List[...],
            "network_out":         List[...],
            "disk_read_bytes":     List[...],
            "disk_write_bytes":    List[...],
            "status_check_failed": List[...],
        },
        "summary": {
            "avg_cpu":    float,
            "avg_memory": float,
        },
    },

    cost={       # populated by CostProvider (DEEP only)
        "currency":              str,    # "USD"
        "granularity":           str,    # "daily"
        "current_month_usd":     float,
        "previous_month_usd":    float,
        "avg_30d_daily_usd":     float,
        "is_idle":               bool,
        "potential_savings_usd": float,
        "daily_breakdown":       List[{"date": str, "amount": float}],
    },

    # ── Analyzer output ────────────────────────────────────
    findings={},         # populated by Analyzers (Phase 3)
    recommendations={},  # populated by RecommendationAnalyzer (Phase 3)

    # ── Internals ──────────────────────────────────────────
    provider_data={      # raw provider envelopes keyed by provider.name
        "resource": {"metadata": {...}, "data": {...}},
        "graph":    {"metadata": {...}, "data": {...}},
        ...
    },
    debug={},
)
```

## ContextLevel Guide

| Level      | Providers that run                                     |
|------------|--------------------------------------------------------|
| `BASIC`    | Resource + Graph + Inventory                           |
| `STANDARD` | BASIC + RelationshipAnalyzer                           |
| `FULL`     | STANDARD + IAM + Documentation                        |
| `DEEP`     | FULL + Metrics + Cost + (future: CloudTrail, Events)   |

## Versioning

- `schema_version` – bump this whenever the `AIContext` shape changes (new fields, removed fields, renamed fields).
- `engine_version` – bump this whenever the engine logic changes (new providers registered, new analysis steps).

Consumers should check `schema_version` to detect format changes.
