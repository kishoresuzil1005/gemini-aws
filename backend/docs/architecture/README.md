# CloudOps AI — Architecture Handbook

> **Version:** 1.0  
> **Status:** Living Document  
> **Maintained by:** Platform Engineering

---

## 📖 What is this?

This directory is the **official architecture documentation** for the CloudOps AI platform.

It contains:

- A **standardized review template** used consistently across all subsystems.
- A **completed review** for each major subsystem.
- **Architectural Decision Records (ADRs)** that explain *why* key design choices were made.
- **Architecture diagrams** for visual reference.

---

## 📐 Standards

| Document | Purpose |
|----------|---------|
| [Architecture_Review_Template.md](standards/Architecture_Review_Template.md) | Official 23‑section template (frozen at v1.0) |
| [Review_Metadata_Header.md](standards/Review_Metadata_Header.md) | Metadata block for every review document |
| [ADR_Guidelines.md](standards/ADR_Guidelines.md) | How to write an Architectural Decision Record |

---

## 📋 Subsystem Reviews

| # | Subsystem | Priority | Status | Document |
|---|-----------|----------|--------|----------|
| 1 | AI Engine | ⭐⭐⭐⭐⭐ | ✅ Completed | [01_AI_Engine.md](subsystems/01_AI_Engine.md) |
| 2 | Graph Assistant | ⭐⭐⭐⭐⭐ | ✅ Completed | [02_Graph_Assistant.md](subsystems/02_Graph_Assistant.md) |
| 3 | Recommendation System | ⭐⭐⭐⭐⭐ | ✅ Completed | [03_Recommendation_System.md](subsystems/03_Recommendation_System.md) |
| 4 | Remediation System | ⭐⭐⭐⭐⭐ | ✅ Completed | [04_Remediation_System.md](subsystems/04_Remediation_System.md) |
| 5 | Orchestration System | ⭐⭐⭐⭐⭐ | ✅ Completed | [05_Orchestration_System.md](subsystems/05_Orchestration_System.md) |
| 6 | Memory System | ⭐⭐⭐⭐ | ✅ Completed | [06_Memory_System.md](subsystems/06_Memory_System.md) |
| 7 | RAG / Knowledge System | ⭐⭐⭐⭐ | ✅ Completed | [07_RAG_System.md](subsystems/07_RAG_System.md) |
| 8 | Response Generation | ⭐⭐⭐⭐ | ✅ Completed | [08_Response_Generation.md](subsystems/08_Response_Generation.md) |
| 9 | LLM Provider Layer | ⭐⭐⭐⭐ | ✅ Completed | [09_LLM_Provider.md](subsystems/09_LLM_Provider.md) |
| 10 | Graph System | ⭐⭐⭐⭐ | ✅ Completed | [10_Graph_System.md](subsystems/10_Graph_System.md) |
| 11 | Inventory System | ⭐⭐⭐⭐ | ✅ Completed | [11_Inventory_System.md](subsystems/11_Inventory_System.md) |
| 12 | Monitoring & Observability | ⭐⭐⭐ | ✅ Completed | [12_Monitoring.md](subsystems/12_Monitoring.md) |
| 13 | Authentication & Security | ⭐⭐⭐ | ✅ Completed | [13_Security.md](subsystems/13_Security.md) |
| 14 | Background Jobs & Workers | ⭐⭐⭐ | ✅ Completed | [14_Background_Jobs.md](subsystems/14_Background_Jobs.md) |

---

## 🗂️ Architectural Decision Records (ADRs)

| ADR | Decision | Status |
|-----|----------|--------|
| [ADR-001](adr/ADR-001-Neo4j.md) | Use Neo4j as the graph database | Accepted |
| [ADR-002](adr/ADR-002-Ollama.md) | Use Ollama as the local LLM provider | Accepted |
| [ADR-003](adr/ADR-003-RAG.md) | Use Qdrant + nomic-embed-text for RAG | Accepted |
| [ADR-004](adr/ADR-004-Conversation_Memory.md) | In-process memory store for conversation context | Accepted |

---

## 🗺️ Diagrams

Place diagrams in the `diagrams/` directory.  
Recommended tools: Draw.io, Mermaid, PlantUML.

---

## 📏 Review Workflow

For each subsystem:

1. **Discover** – `find backend/app -iname "*<subsystem>*"`
2. **Understand** – Read APIs, services, models, data flow, dependencies.
3. **Fill the template** – Use the official 23-section template.
4. **Decide** – ✅ Keep / 🟡 Improve / ❌ Remove.
5. **Update this index** – Change the status from ⏳ to ✅.
6. **Commit** the completed review file.

---

## 🔗 Related Resources

- [Backend README](../../README.md)
- [API Reference](../api/API_REFERENCE.md)
- [Project Repository](https://github.com/kishoresuzil1005/gemini-aws)

---

*Architecture Handbook v1.0 — CloudOps AI Platform*
