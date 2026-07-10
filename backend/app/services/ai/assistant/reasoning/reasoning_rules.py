from typing import Dict, Any

# Severity Weights for Risk Prioritization
SEVERITY_WEIGHTS = {
    "CRITICAL": 100,
    "HIGH": 80,
    "MEDIUM": 50,
    "LOW": 20,
    "INFO": 5,
    "UNKNOWN": 0
}

# Risk Multipliers based on exposure
EXPOSURE_MULTIPLIERS = {
    "PUBLIC": 1.5,
    "INTERNAL": 1.0,
    "ISOLATED": 0.5
}

# Confidence scores for different evidence sources
EVIDENCE_CONFIDENCE = {
    "GraphTool": 1.0, # Ground truth topology
    "SecurityTool": 0.9,
    "InventoryTool": 0.9,
    "CostTool": 0.8,
    "RecommendationTool": 0.7
}

# Conflict Resolution Priorities (Higher wins)
CONFLICT_RESOLUTION_PRIORITY = {
    "GraphTool": 100,
    "InventoryTool": 90,
    "SecurityTool": 80
}

class ReasoningRules:
    @staticmethod
    def get_severity_weight(severity: str) -> int:
        return SEVERITY_WEIGHTS.get(severity.upper(), 0)

    @staticmethod
    def get_exposure_multiplier(exposure: str) -> float:
        return EXPOSURE_MULTIPLIERS.get(exposure.upper(), 1.0)

    @staticmethod
    def get_evidence_confidence(tool_name: str) -> float:
        return EVIDENCE_CONFIDENCE.get(tool_name, 0.5)

    @staticmethod
    def resolve_conflict_winner(tools: list[str]) -> str:
        """
        Returns the tool name that should win based on resolution priority.
        """
        if not tools:
            return "UNKNOWN"
        return max(tools, key=lambda t: CONFLICT_RESOLUTION_PRIORITY.get(t, 0))
