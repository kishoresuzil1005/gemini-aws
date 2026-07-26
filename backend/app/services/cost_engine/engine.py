import logging
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

from app.services.cost_engine.models import (
    CostFinding, CostRecommendation, CostBreakdown,
    CostAttribution, CostAnomaly, CostForecast, CostTrend, IdleResource,
    WasteFinding, RightsizingRecommendation, ReservedInstanceAnalysis,
    SavingsPlanAnalysis, BudgetImpact, BusinessCost, CostRisk, OptimizationOpportunity
)
from app.services.dependency_engine.engine import DependencyIntelligenceEngine
from app.services.security_engine.engine import SecurityIntelligenceEngine
from knowledge.service.knowledge_client import KnowledgeClient

logger = logging.getLogger(__name__)

class CostIntelligenceEngine:
    """Authoritative FinOps Reasoning Engine for the CloudOps Platform."""

    def __init__(self, knowledge_client: KnowledgeClient, dependency_engine: DependencyIntelligenceEngine, security_engine: SecurityIntelligenceEngine):
        self.client = knowledge_client
        self.dep_engine = dependency_engine
        self.sec_engine = security_engine

    def _extract_cost_metadata(self, properties: Dict[str, Any]) -> float:
        """Extracts cost metadata populated by the Knowledge Platform, preventing hardcoding AWS rates."""
        cost = properties.get("monthly_cost", 0.0)
        return float(cost) if cost else 0.0

    def analyze_resource_cost(self, resource_id: str) -> CostBreakdown:
        node = self.dep_engine.get_node(resource_id)
        if not node:
            return CostBreakdown(compute=0, storage=0, network=0, other=0, total=0)
            
        cost = self._extract_cost_metadata(node.properties)
        return CostBreakdown(
            compute=cost if "compute" in node.type.lower() else 0,
            storage=cost if "storage" in node.type.lower() else 0,
            network=cost if "network" in node.type.lower() else 0,
            other=0 if any(t in node.type.lower() for t in ["compute", "storage", "network"]) else cost,
            total=cost
        )

    def analyze_cost_attribution(self, resource_id: str) -> CostAttribution:
        node = self.dep_engine.get_node(resource_id)
        if not node:
            return CostAttribution(team="Unknown", project="Unknown", environment="Unknown", business_unit="Unknown")
            
        tags = node.properties.get("tags", {})
        return CostAttribution(
            team=tags.get("Team", "Unknown"),
            project=tags.get("Project", "Unknown"),
            environment=tags.get("Environment", "Unknown"),
            business_unit=tags.get("BusinessUnit", "Unknown")
        )

    def detect_idle_resources(self, resource_id: str) -> Optional[IdleResource]:
        node = self.dep_engine.get_node(resource_id)
        if not node: return None
        
        # Determine idle state via Knowledge graph properties (e.g., metric extraction attached to node)
        is_idle = False
        if node.type in ["EC2", "RDS"] and "stopped" in str(node.status).lower():
            is_idle = True
        elif node.type == "EBS":
            deps = self.dep_engine.get_dependencies(resource_id)
            if not deps.edges: is_idle = True
            
        if is_idle:
            cost = self._extract_cost_metadata(node.properties)
            return IdleResource(
                resource_id=resource_id,
                type=node.type,
                idle_days=30,  # Simulated extraction from KP
                potential_savings=cost
            )
        return None

    def analyze_waste(self, resource_id: str) -> Optional[WasteFinding]:
        idle = self.detect_idle_resources(resource_id)
        if idle:
            return WasteFinding(
                resource_id=resource_id,
                waste_type="IDLE_RESOURCE",
                wasted_cost=idle.potential_savings,
                reason=f"{idle.type} is unattached or stopped."
            )
        return None

    def generate_optimizations(self, resource_id: str) -> List[CostRecommendation]:
        recs = []
        waste = self.analyze_waste(resource_id)
        if waste:
            recs.append(CostRecommendation(
                title=f"Terminate unused {waste.waste_type}",
                description=waste.reason,
                estimated_savings=waste.wasted_cost,
                optimization_type="TERMINATION",
                effort="LOW",
                affected_resources=[resource_id]
            ))
        return recs

    def analyze_anomaly(self, resource_id: str) -> Optional[CostAnomaly]:
        node = self.dep_engine.get_node(resource_id)
        if not node: return None
        
        # Analyze historical metrics via KP properties
        recent_cost = self._extract_cost_metadata(node.properties)
        avg_cost = node.properties.get("historical_avg_cost", recent_cost)
        if recent_cost > (avg_cost * 1.5) and avg_cost > 0:
            return CostAnomaly(
                resource_id=resource_id,
                spike_amount=recent_cost - avg_cost,
                reason="Cost spiked by 50% above historical average",
                date_detected=datetime.utcnow()
            )
        return None

    def analyze_savings(self, resource_id: str) -> Dict[str, Any]:
        node = self.dep_engine.get_node(resource_id)
        if not node: return {}
        
        cost = self._extract_cost_metadata(node.properties)
        return {
            "spot_savings": cost * 0.7,
            "ri_savings": cost * 0.4
        }

    def generate_business_cost(self, resource_id: str) -> BusinessCost:
        return BusinessCost(
            total_cost=self._extract_cost_metadata(self.dep_engine.get_node(resource_id).properties if self.dep_engine.get_node(resource_id) else {}),
            breakdown=self.analyze_resource_cost(resource_id),
            attribution=self.analyze_cost_attribution(resource_id),
            trends=CostTrend(direction="FLAT", percentage=0.0, period="MONTHLY"),
            forecast=CostForecast(expected_cost=0.0, period="MONTHLY", variance=0.0)
        )

    def generate_ai_explanation(self, cost_obj: BusinessCost, optimizations: List[CostRecommendation]) -> str:
        narrative = "**Executive Cost Summary:**\n"
        narrative += f"Total operational cost is ${cost_obj.total_cost:.2f}. "
        narrative += f"Costs are attributed to Team: {cost_obj.attribution.team}.\n\n"
        
        if optimizations:
            narrative += "**Optimization Narrative:**\n"
            for o in optimizations:
                narrative += f"- {o.title}: Estimated savings of ${o.estimated_savings:.2f}.\n"
        return narrative
