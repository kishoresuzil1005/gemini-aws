# 12 — Monitoring & Observability

| Field | Value |
|-------|-------|
| Review Version | 1.0 |
| Review Date | 2026-07-10 |
| Reviewer | Kishore Suzil |
| Status | Approved |
| Code Version | `13d1019` |

---

## 1. Overview

The Monitoring & Observability subsystem collects CloudWatch metrics, detects anomalies, tracks LLM performance, and provides a `/health` endpoint. It is currently fragmented — metrics collection is in `services/metrics/`, LLM metrics are in `services/ai/assistant/llm/metrics.py`, and anomaly detection is in `services/anomaly/`. There is no centralized observability platform.

---

## 2. Purpose

- **Why it exists:** Provides operational visibility into the CloudOps AI platform and the monitored AWS environment.
- **Primary responsibilities:** AWS CloudWatch metric collection, anomaly detection, LLM request metrics, health endpoints.
- **Never does:** Execute remediations, modify cloud resources.

---

## 3. Architecture Diagram

```mermaid
graph LR
    CW([AWS CloudWatch]) --> MC[MetricsCollector]
    MC --> PostgreSQL[(PostgreSQL)]
    MC --> AJ[AnomalyJob]
    AJ --> AnomalyService[AnomalyService]
    LLM[OllamaProvider] --> MT[MetricsTracker LLM]
    API([FastAPI]) --> Health[/health endpoint]
    Health --> Neo4j[(Neo4j)]
    Health --> Ollama[(Ollama)]
```

---

## 4. Workflow

```
Scheduled job (metric_job.py)
    ↓ MetricsCollector.collect() → boto3 CloudWatch.get_metric_data()
    ↓ PostgreSQL.store(metrics)
    ↓ AnomalyJob.run() → AnomalyService.detect(metrics)
    ↓ anomaly alerts stored or surfaced via API
```

```
OllamaProvider.generate_response()
    ↓ MetricsTracker.record_success(latency_ms)
    ↓ MetricsTracker.record_failure(latency_ms)
    ↓ In-process counters (not exported)
```

---

## 5. Public APIs

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/health` | Platform health check |
| GET | `/api/v1/metrics` | CloudWatch metrics for monitored resources |

---

## 6. Components

| Component | File | Responsibility | Used By | Depends On | Input | Output | Status |
|-----------|------|----------------|---------|------------|-------|--------|--------|
| `MetricsCollector` | `services/metrics/collector.py` | Collects AWS CloudWatch metrics | `metric_job.py` | boto3, PostgreSQL | resource identifiers | stored metrics | 🟡 Improve |
| `AnomalyJob` | `jobs/anomaly_job.py` | Scheduled anomaly detection | Scheduler | `AnomalyService` | metrics | anomaly alerts | 🟡 Improve |
| `MetricJob` | `jobs/metric_job.py` | Scheduled metric collection | Scheduler | `MetricsCollector` | — | — | ✅ Keep |
| `MetricsTracker` (LLM) | `services/ai/assistant/llm/metrics.py` | In-process LLM request metrics | `OllamaProvider` | None | latency, status | counters | 🟡 Export metrics |
| `HealthEndpoint` | `api/health.py` | Platform health check | External monitoring | Neo4j, Ollama | — | `{status, services}` | ✅ Keep |
| `CloudWatchBuilder` | `services/graph/builders/monitoring/cloudwatch.py` | Builds CloudWatch resource nodes in Neo4j | `GraphSyncService` | Neo4j | CloudWatch resources | graph nodes | ✅ Keep |

---

## 7. Data Flow

```
CloudWatch API → MetricsCollector → PostgreSQL
    ↓
AnomalyService.detect(metrics) → anomaly dict
    ↓
API response or alert

OllamaProvider → MetricsTracker → in-process counters (not exported)

FastAPI → /health → Neo4j ping + Ollama ping → {status: "healthy" | "degraded"}
```

---

## 8. Input Models

| Model | Fields | Description |
|-------|--------|-------------|
| resource identifiers | `List[str]` | Resources to collect metrics for |

---

## 9. Output Models

| Model | Fields | Description |
|-------|--------|-------------|
| metrics dict | `{resource_id, metric_name, value, timestamp}` | Collected CloudWatch metrics |
| anomaly alert | `{resource_id, metric, anomaly_type, severity}` | Detected anomaly |
| health response | `{status: str, services: Dict}` | Platform health |

---

## 10. Dependencies

### Internal
- Background jobs scheduler.
- `OllamaProvider` (LLM metrics).

### External
| System | Purpose |
|--------|---------|
| AWS CloudWatch | Source of infrastructure metrics |
| PostgreSQL | Persistent metrics storage |
| Neo4j | Health check |
| Ollama | Health check |

---

## 11. Strengths

- Health endpoint provides a quick operational status check.
- LLM metrics tracking provides latency and error rate visibility.
- CloudWatch integration covers the monitored AWS environment.
- Anomaly detection integrated with background job scheduler.

---

## 12. Weaknesses

- **Fragmented:** Metrics are spread across 3+ separate locations with no unification.
- `MetricsTracker` (LLM) stores data in-process — not exported to any monitoring system.
- No Prometheus endpoint — no integration with Grafana, Datadog, or similar.
- No alerting mechanism — anomalies are detected but not acted upon automatically.
- No distributed tracing (OpenTelemetry).

---

## 13. Current Technical Debt

- [ ] No Prometheus metrics export.
- [ ] `MetricsTracker` is in-process — data lost on restart.
- [ ] No centralized observability platform (Prometheus + Grafana, or CloudWatch + Dashboards).
- [ ] No distributed tracing for AI pipeline requests.
- [ ] Anomaly alerts not integrated with any notification system.

---

## 14. Improvements (Future Work)

- Export metrics to Prometheus via `/metrics` endpoint (Prometheus format).
- Add OpenTelemetry tracing for the full AI pipeline request path.
- Centralize all metrics (LLM, CloudWatch, system) into a single store.
- Integrate anomaly alerts with SNS or PagerDuty.

---

## 15. Roadmap

### Short-Term
- Add Prometheus-compatible `/metrics` endpoint.
- Export `MetricsTracker` counters externally.

### Long-Term
- OpenTelemetry tracing for end-to-end AI request visibility.
- Grafana dashboard for platform and AWS metrics.
- Automated anomaly alert integration.

---

## 16. Testing

| Type | Coverage | Notes |
|------|----------|-------|
| Unit Tests | 0% | Not implemented |
| Integration Tests | 0% | Not implemented |
| API Tests | 0% | Not implemented |
| Performance Tests | 0% | Not implemented |

---

## 17. Production Readiness

| Area | Status | Notes |
|------|--------|-------|
| Logging | 🟡 | Partial logging in collector |
| Metrics | 🟡 | Collected but not exported |
| Retry Logic | ❌ | Not implemented |
| Circuit Breaker | ❌ | Not implemented |
| Monitoring | 🟡 | Health endpoint only |
| Tests | ❌ | No coverage |
| Documentation | ✅ | This document |

---

## 18. Final Verdict

**Decision:** 🟡 Keep and Improve

**Confidence:** 75%

**Priority:** Medium

**Justification:** Functional but fragmented. Primary investment should go into centralizing metrics and adding a Prometheus endpoint.

---

## 19. Design Decisions (ADR)

*No formal ADRs yet for monitoring. Decision to use CloudWatch for infrastructure metrics is implicit given the AWS environment.*

---

## 20. Security Considerations

- `/health` endpoint is public — should not expose sensitive internal details.
- CloudWatch metrics access requires IAM permissions (`cloudwatch:GetMetricData`, `cloudwatch:ListMetrics`).
- Metrics data may contain resource identifiers — stored in PostgreSQL with access controls.

---

## 21. Failure Scenarios

| Failure | Impact | Fallback |
|---------|--------|---------|
| CloudWatch API unavailable | Metric collection fails | Job logs error; no alerts |
| PostgreSQL unavailable | Metrics not persisted | Lost for that collection cycle |
| Ollama unavailable | `/health` returns degraded | Platform continues but AI features disabled |

---

## 22. Performance Characteristics

| Metric | Value |
|--------|-------|
| Metric Collection Frequency | Configurable (default: every 5 minutes) |
| CloudWatch API Latency | 200–500 ms per call |
| Health Check Latency | < 500 ms |

---

## 23. Related Subsystems

| Uses | Used By |
|------|---------|
| AWS CloudWatch | Background Jobs (metric_job.py) |
| PostgreSQL | API routes (/metrics endpoint) |
| LLM Provider Layer (MetricsTracker) | None (in-process only currently) |
