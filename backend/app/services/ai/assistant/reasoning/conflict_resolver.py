import uuid
from typing import List
from app.services.ai.assistant.reasoning.reasoning_models import Finding, Conflict
from app.services.ai.assistant.reasoning.reasoning_rules import ReasoningRules

class ConflictResolver:
    def resolve_conflicts(self, findings: List[Finding]) -> List[Conflict]:
        """
        Detects contradictory findings across tools and resolves them based on priority rules.
        """
        conflicts: List[Conflict] = []
        
        # Stub logic: Identify instances where InventoryTool and SecurityTool contradict
        tools_present = {f.source_tool for f in findings}
        
        if "InventoryTool" in tools_present and "SecurityTool" in tools_present:
            # We simulate detecting a conflict
            winner = ReasoningRules.resolve_conflict_winner(["InventoryTool", "SecurityTool"])
            
            conflict = Conflict(
                id=str(uuid.uuid4()),
                description="Contradictory state between Inventory and Security tools",
                tools_involved=["InventoryTool", "SecurityTool"],
                resolved=True,
                resolution_reason=f"{winner} has higher priority in conflict resolution matrix.",
                winner=winner
            )
            conflicts.append(conflict)
            
        return conflicts
