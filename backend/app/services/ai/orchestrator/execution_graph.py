from typing import List, Dict, Any
from app.services.ai.orchestrator.orchestration_models import ExecutionStep

class ExecutionGraph:
    def build_dag(self, steps: List[ExecutionStep]) -> Dict[str, Any]:
        """
        Builds a Directed Acyclic Graph (DAG) representation of the execution steps.
        For now, this assumes a linear sequential dependency.
        """
        nodes = []
        edges = []
        
        for i, step in enumerate(steps):
            nodes.append({
                "id": step.id,
                "label": step.title,
                "action": step.action
            })
            if i > 0:
                edges.append({
                    "from": steps[i-1].id,
                    "to": step.id,
                    "type": "DEPENDS_ON"
                })
                
        # Add Validation Node at the end
        if nodes:
            val_id = "step-validation"
            nodes.append({
                "id": val_id,
                "label": "Post-Execution Validation",
                "action": "Validate"
            })
            edges.append({
                "from": nodes[-2]["id"],
                "to": val_id,
                "type": "DEPENDS_ON"
            })
            
        return {
            "nodes": nodes,
            "edges": edges
        