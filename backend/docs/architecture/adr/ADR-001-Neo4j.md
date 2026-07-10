# ADR-001: Use Neo4j as the Graph Database

| Field | Value |
|-------|-------|
| Date | 2026-06-25 |
| Status | Accepted |
| Deciders | Kishore Suzil |
| Supersedes | — |

## Context

CloudOps AI needs to model cloud infrastructure as a **connected graph** — EC2 instances connect to VPCs, security groups, subnets, load balancers, RDS instances, and more. Querying multi-hop relationships (e.g., "find all resources that depend on this EC2 instance") is central to blast-radius analysis, criticality scoring, and security analysis. A relational database (PostgreSQL) already stores inventory data but is ill-suited for graph traversal at depth.

## Decision

Use **Neo4j** (community edition) as the dedicated graph database. Relationships are modeled as labeled directed edges. The graph is populated by the `GraphSyncService` and queried by `Neo4jService` using Cypher.

## Rationale

- Native graph traversal with Cypher is orders of magnitude simpler and faster than recursive SQL CTEs.
- Relationship types and node labels map naturally to AWS resource taxonomy.
- Supports rich querying patterns: MATCH, OPTIONAL MATCH, WHERE, COLLECT, and path algorithms (shortest path, all paths).
- Open-source community edition is sufficient for the current scale.

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| PostgreSQL recursive CTEs | Complex queries, poor performance beyond 3 hops. |
| AWS Neptune | Managed but expensive, adds cloud dependency, harder to run locally. |
| NetworkX (in-process) | Does not persist data; not suitable for multi-request scenarios. |

## Consequences

### Positive
- Fast, expressive multi-hop traversal.
- Cypher queries are readable and maintainable.
- Supports future graph algorithms (PageRank, community detection) for advanced criticality scoring.

### Negative
- Additional infrastructure dependency (Neo4j container).
- Requires data synchronization from PostgreSQL/AWS to keep the graph current.
- Engineers must learn Cypher in addition to SQL.

## References

- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/current/)
- [GraphSyncService](../../app/services/graph/graph_sync_service.py)
- [Neo4jService](../../app/services/graph/neo4j_service.py)
