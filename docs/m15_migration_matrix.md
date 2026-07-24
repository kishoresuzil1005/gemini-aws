# M15 Analyzer Migration Matrix

This matrix tracks the migration of all system analyzers from legacy provider-specific logic (e.g. Neo4jService, boto3) to the unified Enterprise Knowledge Platform (KnowledgeClient).

| Analyzer Family | Specific Analyzer | Status | Provider-Agnostic | 
|-----------------|-------------------|--------|-------------------|
| **Dependency** | `DependencyAnalyzer` | Migrated | Yes |
| **Dependency** | `BlastRadiusAnalyzer` | Migrated | Yes |
| **Dependency** | `RootCauseAnalyzer` | Migrated | Yes |
| **Security** | `SecurityImpactAnalyzer` | Migrated | Yes |
| **Security** | `ExposureAnalyzer` | Migrated | Yes |
| **Security** | `SecurityGroupAnalyzer` | Migrated | Yes |
| **Security** | `IAMAnalyzer` | Migrated | Yes |
| **Security** | `NetworkAnalyzer` | Migrated | Yes |
| **Security** | `AttackPathAnalyzer` | Migrated | Yes |
| **Cost** | `CostAnalyzer` | Migrated | Yes |
| **Architecture**| `ArchitectureReviewer` | Migrated | Yes |
| **Criticality** | `CriticalityAnalyzer` | Migrated | Yes |
| **Migration** | `MigrationPlanner` | Migrated | Yes |
| **AI Query** | `NLQueryEngine` | Migrated | Yes |
| **AI Graph** | `AIGraphAgent` | Migrated | Yes |

## Supporting Engines

| Engine | Component | Status | Provider-Agnostic |
|--------|-----------|--------|-------------------|
| **Context** | `ServiceContainer` | Migrated | Yes |
| **Context** | `GraphProvider` | Migrated | Yes |
| **Context** | `IAMProvider` | Migrated | Yes |
| **Context** | `InventoryProvider` | Migrated | Yes |
| **Context** | `MetricsProvider` | Migrated | Yes |
| **Context** | `CostProvider` | Migrated | Yes |
| **Context** | `DocumentationProvider` | Migrated | Yes |
| **Graph** | `GraphAdapter` | Migrated | Yes |
| **Recommendation** | `AIRecommendationEngine` | Migrated | Yes |

## Summary
All direct dependencies on Neo4jService, Boto3, and internal PostgreSQL instances have been removed from the analyzer logic. The Enterprise Knowledge Platform acts as the single source of truth for all resource, relationship, and rule evaluations across the system.
