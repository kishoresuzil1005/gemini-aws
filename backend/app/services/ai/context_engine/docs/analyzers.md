# Analyzers Reference

## Design Rules

1. Analyzers are **stateless** – instantiate fresh per request.
2. Analyzers **never call providers or external APIs** – they work only on `AIContext`.
3. Analyzers **never modify** the `AIContext` they receive.
4. Analyzer output goes into `AIContext.findings` and `AIContext.recommendations`.

## BaseAnalyzer

```python
class BaseAnalyzer(ABC):
    name: str

    @abstractmethod
    def analyze(self, context: AIContext) -> Dict[str, Any]:
        ...
```

## RelationshipAnalyzer (FULLY IMPLEMENTED)

The only fully implemented analyzer in Phase 2.

```python
from app.services.ai.context_engine.analyzers import RelationshipAnalyzer

ra = RelationshipAnalyzer()
result = ra.analyze(context)
```

### Methods

| Method                         | Description                                       |
|--------------------------------|---------------------------------------------------|
| `get_downstream(ctx, node_id)` | Resources that depend on the given node           |
| `get_upstream(ctx, node_id)`   | Resources the given node depends on               |
| `compute_blast_radius(ctx, id)`| All nodes affected if the given node fails        |
| `shortest_path(ctx, src, tgt)` | Shortest connection between two nodes             |
| `detect_cycles(ctx)`           | Circular dependencies in the graph                |
| `dependency_depth(ctx, id)`    | Max depth of the dependency tree                  |
| `reachable_nodes(ctx, id)`     | All reachable nodes (any direction)               |
| `find_single_points_of_failure(ctx)` | Nodes whose removal disconnects the graph   |

### Return shape

```python
{
    "downstream":               ["sg-001", "alb-001"],
    "upstream":                 [],
    "blast_radius":             ["sg-001", "alb-001", "rds-001"],
    "cycles":                   [],
    "dependency_depth":         3,
    "reachable_nodes":          ["sg-001", "alb-001", "rds-001"],
    "single_points_of_failure": ["alb-001"],
}
```

## RecommendationAnalyzer (STUB)

```python
from app.services.ai.context_engine.analyzers import RecommendationAnalyzer

ra = RecommendationAnalyzer()
recs = ra.generate(context)  # → List[Dict]
```

Planned output shape per recommendation:

```python
{
    "id":          "rec-001",
    "severity":    "high",          # critical | high | medium | low
    "category":    "security",      # security | cost | reliability | ...
    "title":       "Overly permissive IAM role",
    "description": "...",
    "remediation": "...",
    "source":      "security_analyzer",
    "resource_id": "i-0abc123",
}
```

## Stub Analyzers (Phase 3)

| Analyzer                 | Category      | Status  |
|--------------------------|---------------|---------|
| TopologyAnalyzer         | architecture  | stub    |
| BlastRadiusAnalyzer      | reliability   | stub    |
| DependencyAnalyzer       | architecture  | stub    |
| ArchitectureAnalyzer     | architecture  | stub    |
| SecurityAnalyzer         | security      | stub    |
| CostAnalyzer             | cost          | stub    |
| PerformanceAnalyzer      | performance   | stub    |
| MigrationAnalyzer        | migration     | stub    |
| ReliabilityAnalyzer      | reliability   | stub    |
| ComplianceAnalyzer       | compliance    | stub    |
| DisasterRecoveryAnalyzer | disaster_recovery | stub |
