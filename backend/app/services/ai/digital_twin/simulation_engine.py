"""Simulation Engine — Phase 5"""
from __future__ import annotations
from typing import Any, Dict, List
from .twin_db import DigitalTwinDB


class SimulationEngine:
    """
    Simulates infrastructure changes against the digital twin
    without touching production systems.
    """

    def __init__(self):
        self._db = DigitalTwinDB()

    def simulate(self, resource_id: str, proposed_change: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply proposed_change to the digital twin snapshot and return
        the predicted resulting state + list of side effects.
        """
        current = self._db.get(resource_id)
        if not current:
            return {"error": f"No digital twin snapshot found for {resource_id}"}

        simulated_state = dict(current.get("data", {}))
        simulated_state.update(proposed_change)

        side_effects: List[str] = []
        if proposed_change.get("stop"):
            side_effects.append("All traffic to this instance will stop")
        if proposed_change.get("security_group"):
            side_effects.append("Network access rules will change")
        if proposed_change.get("terminate"):
            side_effects.append("Persistent EBS volumes may be lost unless detached")

        return {
            "resource_id": resource_id,
            "current_state": current.get("data"),
            "simulated_state": simulated_state,
            "side_effects": side_effects,
            "safe_to_apply": len(side_effects) == 0,
        }
