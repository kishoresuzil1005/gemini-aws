import time
from typing import Dict, Any

class ProviderMetrics:
    """Tracks API latency, failures, success rates, and retries per provider."""
    
    def __init__(self):
        # A real implementation would push these to Prometheus / Datadog
        self.metrics: Dict[str, Dict[str, Any]] = {
            "AWS": {"total_calls": 0, "successes": 0, "failures": 0, "total_latency_ms": 0.0},
            "AZURE": {"total_calls": 0, "successes": 0, "failures": 0, "total_latency_ms": 0.0},
            "GCP": {"total_calls": 0, "successes": 0, "failures": 0, "total_latency_ms": 0.0},
            "KUBERNETES": {"total_calls": 0, "successes": 0, "failures": 0, "total_latency_ms": 0.0}
        }

    def record_call(self, provider: str, success: bool, latency_ms: float):
        if provider not in self.metrics:
            self.metrics[provider] = {"total_calls": 0, "successes": 0, "failures": 0, "total_latency_ms": 0.0}
            
        self.metrics[provider]["total_calls"] += 1
        if success:
            self.metrics[provider]["successes"] += 1
        else:
            self.metrics[provider]["failures"] += 1
            
        self.metrics[provider]["total_latency_ms"] += latency_ms

    def get_success_rate(self, provider: str) -> float:
        stats = self.metrics.get(provider)
        if not stats or stats["total_calls"] == 0:
            return 100.0
        return (stats["successes"] / stats["total_calls"]) * 100.0

# Global instance for tracking across the lifecycle
metrics_tracker = ProviderMetrics()
