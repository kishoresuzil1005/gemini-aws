from app.services.graph.analysis.criticality import CriticalityAnalyzer

class CriticalityService:
    def __init__(self):
        self.analyzer = CriticalityAnalyzer()

    def calculate(self, resource_id: str):
        return self.analyzer.analyze(resource_id)

    def top_critical(self):
        # We'll improve this in Sprint 8.5
        return []
