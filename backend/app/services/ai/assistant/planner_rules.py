from typing import Dict, List, Any

# Phase 3 Recommendation #1: Make planning data-driven
INTENT_OBJECTIVE_MAP = {
    "SECURITY": "Analyze security vulnerabilities, IAM misconfigurations, and external exposure.",
    "COST": "Analyze underutilized resources, compute waste, and optimization opportunities.",
    "TROUBLESHOOT": "Identify root causes, dependent failures, and recent configuration changes.",
    "DEPENDENCY": "Map incoming and outgoing network/IAM dependencies.",
    "INVENTORY": "List and describe resources matching criteria."
}

INTENT_TOOL_MAP = {
    "SECURITY": ["GraphTool", "SecurityTool", "BlastRadiusTool", "RecommendationTool"],
    "COST": ["GraphTool", "CostTool", "RecommendationTool"],
    "TROUBLESHOOT": ["GraphTool", "DependencyTool", "RootCauseTool", "RecommendationTool"],
    "DEPENDENCY": ["GraphTool", "DependencyTool"],
    "INVENTORY": ["InventoryTool"],
    "DOCUMENTATION": ["DocumentationTool"]
}

class PlannerRules:
    @staticmethod
    def get_objective(intent: str) -> str:
        return INTENT_OBJECTIVE_MAP.get(intent, "Fulfill user request by analyzing cloud environment.")

    @staticmethod
    def get_tools(intent: str) -> List[str]:
        return INTENT_TOOL_MAP.get(intent, ["GraphTool"]