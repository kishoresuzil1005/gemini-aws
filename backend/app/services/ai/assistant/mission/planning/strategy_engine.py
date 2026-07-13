from enum import Enum
from typing import Dict, Any

class ExecutionStrategy(str, Enum):
    CONSERVATIVE = "CONSERVATIVE"
    BALANCED = "BALANCED"
    AGGRESSIVE = "AGGRESSIVE"

class StrategyEngine:
    """
    Determines the velocity and risk-tolerance for mission execution.
    """
    def determine_strategy(self, intent: str, context: Dict[str, Any]) -> ExecutionStrategy:
        if "production" in str(context).lower() or "critical" in intent.lower():
            return ExecutionStrategy.CONSERVATIVE
        return ExecutionStrategy.BALANCE