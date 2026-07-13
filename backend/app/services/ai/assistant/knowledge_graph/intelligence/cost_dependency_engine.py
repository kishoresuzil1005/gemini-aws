from typing import Dict, List
from app.services.ai.assistant.knowledge_graph.query.graph_traversal import GraphTraversal

class CostDependencyEngine:
    """
    Evaluates FinOps impact across dependent resources.
    Example: Deleting a NAT Gateway saves $X but alters Data Transfer Costs across Y connected subnets.
    """
    
    def __init__(self, traversal: GraphTraversal):
        self.traversal = traversal
        
    def calculate_cost_impact(self, target_node_id: str, action: str) -> Dict[str, any]:
        """Balances infrastructure risk vs cost savings."""
        affected_nodes = self.traversal.get_blast_radius_subgraph(target_node_id, max_depth=1)
        
        # Simulated cost logic
        direct_savings = 0.0
        indirect_costs = 0.0
        
        if action.upper() == "DELETE":
            direct_savings = 50.0  # e.g., standard baseline savings
            
        return {
            "target": target_node_id,
            "action": action,
            "direct_monthly_savings_usd": direct_savings,
            "indirect_monthly_costs_usd": indirect_costs,
            "net_impact_usd": direct_savings - indirect_costs,
            "affected_financial_nodes": len(affected_nodes)
        }