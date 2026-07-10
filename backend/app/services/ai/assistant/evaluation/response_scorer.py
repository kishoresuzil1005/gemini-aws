from typing import Dict, Any

class ResponseScorer:
    """
    Evaluates LLM response quality across accuracy, grounding, completeness, and latency.
    """
    def score(self, question: str, answer: str, sources: list, latency_ms: int) -> Dict[str, Any]:
        grounding_score = min(100, len(sources) * 15)
        completeness_score = min(100, len(answer) // 10)
        latency_score = 100 if latency_ms < 3000 else max(0, 100 - (latency_ms - 3000) // 100)

        overall = (grounding_score + completeness_score + latency_score) // 3

        return {
            "grounding": grounding_score,
            "completeness": completeness_score,
            "latency_ms": latency_ms,
            "latency_score": latency_score,
            "overall": overall,
            "grade": "A" if overall >= 85 else "B" if overall >= 70 else "C"
        }
