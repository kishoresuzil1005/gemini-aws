class MetricsTracker:
    # A simple in-memory tracker for demonstration. In production, this would use Prometheus/Datadog.
    _metrics = {
        "llm_requests": 0,
        "llm_success": 0,
        "llm_failure": 0,
        "total_latency_ms": 0
    }

    @classmethod
    def record_success(cls, latency_ms: int):
        cls._metrics["llm_requests"] += 1
        cls._metrics["llm_success"] += 1
        cls._metrics["total_latency_ms"] += latency_ms

    @classmethod
    def record_failure(cls, latency_ms: int):
        cls._metrics["llm_requests"] += 1
        cls._metrics["llm_failure"] += 1
        cls._metrics["total_latency_ms"] += latency_ms

    @classmethod
    def get_metrics(cls):
        requests = cls._metrics["llm_requests"]
        avg_latency = cls._metrics["total_latency_ms"] / requests if requests > 0 else 0
        return {
            "llm_requests": requests,
            "llm_success": cls._metrics["llm_success"],
            "llm_failure": cls._metrics["llm_failure"],
            "avg_latency_ms": round(avg_latency, 2)
        }
