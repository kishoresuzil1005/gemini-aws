from typing import Dict, Any
from collections import defaultdict
from datetime import datetime

class AIMetricsCollector:
    """
    Extends the existing MetricsTracker in llm/metrics.py with platform-level
    AI observability metrics: token usage, model distribution, cache hits,
    grounding scores, and hallucination rates.
    
    In production, this flushes to Prometheus via the monitoring/opentelemetry.py layer.
    """
    def __init__(self):
        self._requests: int = 0
        self._failures: int = 0
        self._total_latency_ms: int = 0
        self._total_input_tokens: int = 0
        self._total_output_tokens: int = 0
        self._cache_hits: int = 0
        self._hallucination_warnings: int = 0
        self._grounding_scores: list = []
        self._model_usage: Dict[str, int] = defaultdict(int)
        self._intent_distribution: Dict[str, int] = defaultdict(int)

    def record_request(self, model: str, intent: str, latency_ms: int,
                       input_tokens: int = 0, output_tokens: int = 0,
                       success: bool = True, cache_hit: bool = False,
                       grounding_score: float = 0.0, hallucination_warning: bool = False):
        self._requests += 1
        if not success:
            self._failures += 1
        self._total_latency_ms += latency_ms
        self._total_input_tokens += input_tokens
        self._total_output_tokens += output_tokens
        self._model_usage[model] += 1
        self._intent_distribution[intent] += 1
        if cache_hit:
            self._cache_hits += 1
        if hallucination_warning:
            self._hallucination_warnings += 1
        if grounding_score > 0:
            self._grounding_scores.append(grounding_score)

    def get_summary(self) -> Dict[str, Any]:
        avg_latency = self._total_latency_ms / self._requests if self._requests > 0 else 0
        avg_grounding = sum(self._grounding_scores) / len(self._grounding_scores) if self._grounding_scores else 0
        hallucination_rate = (self._hallucination_warnings / self._requests * 100) if self._requests > 0 else 0

        return {
            "total_requests": self._requests,
            "failures": self._failures,
            "success_rate_pct": round(((self._requests - self._failures) / max(self._requests, 1)) * 100, 2),
            "avg_latency_ms": round(avg_latency, 2),
            "total_input_tokens": self._total_input_tokens,
            "total_output_tokens": self._total_output_tokens,
            "cache_hits": self._cache_hits,
            "cache_hit_rate_pct": round((self._cache_hits / max(self._requests, 1)) * 100, 2),
            "avg_grounding_score": round(avg_grounding, 3),
            "hallucination_warnings": self._hallucination_warnings,
            "hallucination_rate_pct": round(hallucination_rate, 2),
            "model_usage": dict(self._model_usage),
            "intent_distribution": dict(self._intent_distribution),
            "recorded_at": datetime.utcnow().isoformat()
        }


# Singleton collector
ai_metrics = AIMetricsCollector(