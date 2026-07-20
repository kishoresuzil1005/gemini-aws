# AI architecture

The chat system has one cloud-context path:

`ConversationManager → IntentClassifier → QueryResolver → ExecutionContext → ContextRequest → ContextEngine → AIContext → ReasoningEngine → PromptBuilder → ResponseGenerator`

## Boundaries

- `QueryResolver` identifies a resource; it does not call cloud APIs or an LLM.
- `ExecutionContext` is immutable assistant request state. `ContextRequest` is the smaller reusable request supplied to `ContextEngine`.
- `ContextEngine` is the sole collector of cloud data. Providers may call AWS, Neo4j, databases, or caches.
- `AnalysisEngine` runs only against the assembled `AIContext` and records deterministic findings and recommendations there.
- `ReasoningEngine` interprets `AIContext`; it does not fetch data or format prompts.
- `PromptBuilder` transforms `AIContext` plus `ReasoningResult` into model messages; it performs no data lookup or reasoning.
- `ResponseGenerator` is the only component that communicates with the LLM.

## Extension rules

Add a cloud data source by implementing and registering a Context Engine provider. Add deterministic intelligence by implementing a context analyzer. Do not add assistant tools, graph retrievers, context builders, planners, or alternate prompt pipelines.
