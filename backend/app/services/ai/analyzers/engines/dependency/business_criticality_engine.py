"""
Business Criticality Engine.
Deterministically classifies resource business criticality based on topology, environment, and tags.
"""
from typing import Dict, Any

class BusinessCriticalityEngine:
    
    @classmethod
    def calculate(cls, props: Dict[str, Any], blast_radius: int, upstream_count: int) -> Dict[str, Any]:
        """
        Classifies resources as Mission Critical, Production, Customer Facing, Internal,
        Shared Platform, Development, Testing, Sandbox, or Disaster Recovery.
        Returns the tier and multidimensional scores.
        """
        tags = props.get("tags", {})
        
        # 1. Evaluate Environment
        env = str(tags.get("Environment", tags.get("environment", "Unknown"))).lower()
        if env in ["sandbox"]:
            tier = "Sandbox"
        elif env in ["dev", "development"]:
            tier = "Development"
        elif env in ["test", "testing", "qa"]:
            tier = "Testing"
        elif env in ["dr", "disaster recovery", "failover"]:
            tier = "Disaster Recovery"
        else:
            tier = "Internal"
            
        # 2. Evaluate Tier & Application
        # 2. Evaluate Tier & Application
        tier_tag = str(tags.get("Tier", tags.get("tier", ""))).lower()
        if tier_tag == "mission-critical" or tier_tag == "tier0" or tier_tag == "tier-0":
            tier = "Mission Critical"
            
        # 3. Assess Topology Blast Radius
        if env in ["prod", "production"]:
            if blast_radius > 50:
                tier = "Mission Critical"
            elif blast_radius > 10:
                tier = "Customer Facing"
            else:
                tier = "Production"
            
        # 4. Assess Upstream Dependencies (Shared Platform)
        if upstream_count > 20:
            tier = "Shared Platform"
            
        # 5. Default Fallbacks based on Resource Type
        rtype = props.get("type", props.get("resource_type", "Unknown"))
        if rtype in ["VPC", "InternetGateway", "DirectConnect"] and tier == "Internal":
            tier = "Shared Platform"
            
        # Multi-dimensional Importance Scores
        importance = {
            "business_importance": 100 if tier in ["Mission Critical", "Customer Facing", "Production"] else 50,
            "availability_importance": 100 if tier in ["Mission Critical", "Shared Platform"] else 60,
            "security_importance": 100 if tier in ["Mission Critical", "Customer Facing"] else 75,
            "compliance_importance": 100 if "prod" in env else 50,
            "operational_importance": 100 if tier in ["Shared Platform", "Mission Critical"] else 50
        }
            
        return {
            "tier": tier,
            "scores": importance
        }
