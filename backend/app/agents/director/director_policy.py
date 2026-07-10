from typing import Dict, Any, List

class DirectorPolicy:
    """
    Defines the rules for agent participation, e.g., only involving Security Agent
    if the risk level is > LOW.
    """
    def determine_required_domains(self, workflow_context: Dict[str, Any]) -> List[str]:
        domains = ["workflow"]
        if workflow_context.get("involves_infrastructure", False):
            domains.append("infrastructure")
        if workflow_context.get("risk_level", "LOW") != "LOW":
            domains.append("security")
            
        return domains
