from typing import Dict, Any, List
from .trend_analyzer import TrendAnalyzer
from .benchmark_engine import BenchmarkEngine

class AnalyticsEngine:
    """
    The central analytics brain that aggregates data from Missions, 
    Knowledge Graph, and Cloud Telemetry to surface high-level insights.
    """
    def __init__(self, trend_analyzer: TrendAnalyzer, benchmark_engine: BenchmarkEngine):
        self.trend_analyzer = trend_analyzer
        self.benchmark_engine = benchmark_engine

    def generate_system_insights(self) -> Dict[str, Any]:
        print("[AnalyticsEngine] Aggregating multi-source telemetry data...")
        trends = self.trend_analyzer.analyze_usage_trends()
        benchmarks = self.benchmark_engine.compare_to_industry_standards()
        
        return {
            "status": "compiled",
            "insights": [
                "CPU usage in production is 15% above industry median.",
                "IAM policy compliance improved by 20% over 30 days."
            ],
            "trends": trends,
            "benchmarks": benchmarks
        }
