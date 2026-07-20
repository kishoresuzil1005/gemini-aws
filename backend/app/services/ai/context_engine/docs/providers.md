# Providers Reference

## Standard Response Envelope

Every provider must return:

```python
{
    "metadata": {
        "provider":         str,    # provider.name
        "version":          str,    # provider.version
        "generated_at":     str,    # ISO-8601 UTC
        "cache_ttl":        int,    # seconds
        "status":           str,    # "ok" | "error" | "not_implemented"
        "enabled":          bool,
        "execution_time_ms": float,
        "source":           str,    # "postgres" | "neo4j" | "cloudwatch" ...
    },
    "data": { ... }  # provider-specific payload
}
```

## Concrete Providers

### ResourceProvider
- **Priority**: 0 (always first)
- **Output key**: `resource`
- **Source**: PostgreSQL → `resources` table
- **Supports**: all levels
- **Returns**: `id`, `name`, `type`, `provider`, `region`, `account`, `arn`, `status`, `tags`

### GraphProvider
- **Priority**: 10
- **Output key**: `graph`
- **Source**: Neo4j (+ MemoryGraphStore fallback)
- **Supports**: all levels
- **Returns**: `resource` (root node), `nodes` (all), `edges` (all), `subgraph` (1-hop)

### InventoryProvider
- **Priority**: 20
- **Output key**: `inventory`
- **Source**: PostgreSQL → `resources` + `cloud_accounts`
- **Supports**: all levels
- **Returns**: `resource_id`, `account_id`, `organization`, `environment`, `project`, `region`, `provider`, `owner`, `tags`, `metadata`, `scanner_version`, `last_discovered`

### IAMProvider
- **Priority**: 30
- **Output key**: `security`
- **Source**: AWS IAM API (boto3)
- **Supports**: `FULL`, `DEEP` only
- **Returns**: `identities`, `permissions`, `trust_relationships`, `permission_boundaries`
- **Note**: Resolves EC2 instance profile → role automatically

### DocumentationProvider
- **Priority**: 40
- **Output key**: `documentation`
- **Source**: Internal DB → Qdrant → AWS Docs (in priority order)
- **Supports**: `FULL`, `DEEP` only
- **Returns**: `sources` (list of doc entries), `primary_source`

### MetricsProvider
- **Priority**: 50
- **Output key**: `metrics`
- **Source**: AWS CloudWatch (boto3)
- **Supports**: `DEEP` only
- **Returns**: `look_back_hours`, `period_seconds`, `datapoints` (7 metric streams), `summary`
- **Configurable**: `ContextRequest.metrics_look_back` (default 24h)

### CostProvider
- **Priority**: 60
- **Output key**: `cost`
- **Source**: AWS Cost Explorer (via `CostExplorerAdapter`)
- **Supports**: `DEEP` only
- **Returns**: `currency`, `granularity`, `current_month_usd`, `previous_month_usd`, `avg_30d_daily_usd`, `is_idle`, `potential_savings_usd`, `daily_breakdown`
- **Idle threshold**: < $0.10/day avg

## Placeholder Providers (Phase 3)

| Provider             | Priority | Output Key   | Source         |
|----------------------|----------|--------------|----------------|
| CloudTrailProvider   | 70       | `events`     | AWS CloudTrail |
| EventBridgeProvider  | 80       | `events`     | AWS EventBridge|
| ConfigProvider       | 90       | `compliance` | AWS Config     |
| HealthProvider       | 100      | `health`     | AWS Health     |

All placeholders return `status="not_implemented"` and `enabled=False`.
