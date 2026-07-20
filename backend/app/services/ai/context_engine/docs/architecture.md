# AI Context Engine – Architecture Overview

## Purpose

The **Context Engine** is the data-gathering layer of the AI platform. It
assembles a canonical `AIContext` object containing everything the LLM needs
to understand a cloud resource before generating recommendations.

```
User / API
    │
    ▼
ContextEngine.build(request)
    │
    ▼
PipelineFactory ──► PipelineConfiguration
    │
    ▼
ContextPipeline
    │
    ├── ResourceResolver   (identifier → ResolvedResource)
    │
    ├── ProviderManager    (sorted by priority, respects feature flags)
    │       │
    │       ├── ResourceProvider     priority=0   → ctx.resource
    │       ├── GraphProvider        priority=10  → ctx.graph
    │       ├── InventoryProvider    priority=20  → ctx.inventory
    │       ├── IAMProvider          priority=30  → ctx.security
    │       ├── DocumentationProvider priority=40 → ctx.documentation
    │       ├── MetricsProvider      priority=50  → ctx.metrics
    │       ├── CostProvider         priority=60  → ctx.cost
    │       └── [Placeholder providers …]
    │
    └── ContextAssembler   (payloads → AIContext)
            │
            ▼
         AIContext
```

## Core Design Rules

1. **Providers only collect facts** – no analysis, no scoring, no thresholds.
2. **Analyzers derive conclusions** – operating only on the assembled `AIContext`.
3. **Context levels are cumulative** – `DEEP ⊃ FULL ⊃ STANDARD ⊃ BASIC`.
4. **Feature flags control each provider** – set env vars to enable/disable.
5. **Providers are sorted by priority** – lower number runs first.
6. **Every provider returns a standard envelope** – `{"metadata": {...}, "data": {...}}`.

## Files

```
context_engine/
│
├── engine.py            ← Public entry point: ContextEngine
├── pipeline.py          ← Orchestrates end-to-end flow
├── pipeline_factory.py  ← Builds configured pipelines
├── provider_manager.py  ← Runs providers (caching, error handling)
├── assembler.py         ← Merges payloads into AIContext
├── registry.py          ← ProviderRegistry + register_default_providers()
├── resolver.py          ← Resolves identifiers → ResolvedResource
├── cache.py             ← MemoryCache (pluggable CacheBackend)
├── configuration.py     ← PipelineConfiguration dataclass
├── request.py           ← ContextRequest Pydantic model
├── models.py            ← AIContext + ExecutionMetadata
├── enums.py             ← ContextLevel, ProviderScope
├── exceptions.py        ← Exception hierarchy
├── base_provider.py     ← BaseProvider ABC
│
├── common/              ← Shared utilities
│   ├── constants.py     ← Feature-flag names, TTL defaults, versions
│   ├── helpers.py       ← iso_timestamp(), flag_enabled(), elapsed_ms()
│   ├── types.py         ← TypedDicts for provider payloads
│   ├── validators.py    ← Input validation helpers
│   ├── cache_keys.py    ← Cache key builders
│   └── time.py          ← utcnow(), look_back_range()
│
├── providers/           ← Concrete provider implementations
│   ├── resource_provider.py     ← PostgreSQL → resource identity
│   ├── graph_provider.py        ← Neo4j → topology (nodes, edges)
│   ├── inventory_provider.py    ← PostgreSQL → CMDB metadata
│   ├── iam_provider.py          ← AWS IAM → normalized IAM snapshot
│   ├── documentation_provider.py← Internal + Qdrant + AWS docs
│   ├── metrics_provider.py      ← CloudWatch → performance metrics
│   ├── cost_provider.py         ← Cost Explorer → cost summary
│   └── [placeholder providers]  ← CloudTrail, EventBridge, Config, Health
│
├── analyzers/           ← Derived analysis (operate on AIContext)
│   ├── base_analyzer.py
│   ├── relationship_analyzer.py ← FULL implementation (8 methods)
│   ├── recommendation_analyzer.py
│   └── [11 stub analyzers]
│
├── tests/               ← Integration tests
│   └── test_context_engine_e2e.py
│
└── docs/                ← This documentation
    ├── architecture.md  ← You are here
    ├── providers.md
    ├── analyzers.md
    └── aicontext.md
```

## Provider Execution Flow

```
ProviderManager.run(resource, request, exec_meta)
    │
    ├── Sort providers by priority (ascending)
    │
    ├── For each provider:
    │   ├── Check provider.enabled (feature flag)
    │   ├── Check provider.supports(request.level)
    │   ├── Check cache (provider_cache_key)
    │   ├── Call provider.fetch(resource, request)
    │   ├── Cache the result
    │   └── Record in exec_meta.providers_executed
    │
    └── Return Dict[provider_name, payload]
```

## AIContext Structure

```python
AIContext(
    metadata={
        "schema_version": "1.0",
        "engine_version":  "1.0.0",
        "generated_at":    "ISO-8601",
        "context_level":   "full",
    },
    execution=ExecutionMetadata(
        providers_executed=["resource", "graph", ...],
        providers_failed=[],
        cache_hits=0,
        duration_seconds=0.123,
    ),
    resource={...},        # ← ResourceProvider
    graph={...},           # ← GraphProvider
    inventory={...},       # ← InventoryProvider
    security={...},        # ← IAMProvider
    documentation={...},   # ← DocumentationProvider
    metrics={...},         # ← MetricsProvider
    cost={...},            # ← CostProvider
    findings={},           # ← Populated by Analyzers (Phase 3)
    recommendations={},    # ← Populated by RecommendationAnalyzer (Phase 3)
    provider_data={...},   # ← Raw provider envelopes for debugging
    debug={},
)
```

## Debug Endpoint

```
GET /api/v1/ai/context/{resource_id}?level=basic
```

Returns the assembled `AIContext` as JSON. Useful for:
- Verifying provider data shapes
- Checking feature flag configuration
- Integration testing without a frontend

Valid levels: `basic`, `standard`, `full`, `deep`

## Feature Flags

| Environment Variable             | Default | Provider              |
|----------------------------------|---------|----------------------|
| `RESOURCE_PROVIDER_ENABLED`      | `true`  | ResourceProvider     |
| `GRAPH_PROVIDER_ENABLED`         | `true`  | GraphProvider        |
| `INVENTORY_PROVIDER_ENABLED`     | `true`  | InventoryProvider    |
| `IAM_PROVIDER_ENABLED`           | `true`  | IAMProvider          |
| `DOCUMENTATION_PROVIDER_ENABLED` | `true`  | DocumentationProvider|
| `METRICS_PROVIDER_ENABLED`       | `true`  | MetricsProvider      |
| `COST_PROVIDER_ENABLED`          | `true`  | CostProvider         |
| `CLOUDTRAIL_PROVIDER_ENABLED`    | `false` | CloudTrailProvider   |
| `EVENTBRIDGE_PROVIDER_ENABLED`   | `false` | EventBridgeProvider  |
| `CONFIG_PROVIDER_ENABLED`        | `false` | ConfigProvider       |
| `HEALTH_PROVIDER_ENABLED`        | `false` | HealthProvider       |

## Adding a New Provider

1. Create `providers/my_provider.py` extending `BaseProvider`.
2. Set `name`, `output_key`, `priority`, `enabled`, `version`, `source`.
3. Implement `supports(level)` and `async fetch(resource, request)`.
4. Return `self._build_response(data, execution_time_ms=exec_ms)`.
5. Add the import to `providers/__init__.py`.
6. Add `MyProvider()` to `register_default_providers()` in `registry.py`.
7. Add a feature flag constant to `common/constants.py`.
8. Add the corresponding field to `AIContext` in `models.py` if needed.
