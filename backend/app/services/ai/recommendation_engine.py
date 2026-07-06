from typing import List, Dict, Any
from pydantic import BaseModel
from app.services.graph.neo4j_service import Neo4jService
from app.services.graph.analysis.security.orchestrator import SecurityImpactAnalyzer
from app.services.graph.analysis.criticality import CriticalityAnalyzer

class Recommendation(BaseModel):
    issue_title: str
    resource_id: str
    resource_type: str
    reasons: List[str]
    recommendation_text: str
    priority: str
    category: str
    estimated_impact: str

class AIRecommendationEngine:
    def __init__(self, neo4j_service: Neo4jService = None):
        self.neo4j = neo4j_service or Neo4jService()
        self.security_analyzer = SecurityImpactAnalyzer(self.neo4j)
        self.criticality_analyzer = CriticalityAnalyzer(self.neo4j)
        
    def _determine_resource_type(self, resource_id: str) -> str:
        if self.neo4j.driver:
            try:
                res = self.neo4j.query("MATCH (n {id:$resource_id}) RETURN labels(n)[0] as type", resource_id=resource_id)
                if res and res[0].get("type"):
                    return res[0]["type"]
            except Exception:
                pass
        return "Unknown"

    def analyze_resource(self, resource_id: str) -> List[Recommendation]:
        """
        Consumes graph analyses for a specific resource and synthesizes actionable recommendations.
        """
        recommendations = []
        resource_type = self._determine_resource_type(resource_id)
        
        # 1. Fetch Security Analysis
        try:
            sec_analysis = self.security_analyzer.analyze(resource_id)
        except Exception:
            sec_analysis = {}
            
        # 2. Fetch Criticality Analysis
        try:
            crit_analysis = self.criticality_analyzer.analyze(resource_id)
            crit_level = crit_analysis.get("criticality_level", "LOW")
        except Exception:
            crit_level = "LOW"
            
        # Generate Security Recommendations
        if sec_analysis:
            reasons = sec_analysis.get("reason", [])
            for finding in sec_analysis.get("findings", []):
                f_type = finding.get("type", "")
                severity = finding.get("severity", "LOW")
                
                # Boost priority based on resource criticality
                priority = severity
                if crit_level in ["HIGH", "CRITICAL"] and severity in ["MEDIUM", "HIGH"]:
                    priority = "CRITICAL"
                    
                if f_type in ["PUBLIC_ACCESS", "NETWORK_PUBLIC", "PUBLIC_SUBNET", "INTERNET_FACING"]:
                    recommendations.append(Recommendation(
                        issue_title=f"Public Exposure on {resource_type}",
                        resource_id=resource_id,
                        resource_type=resource_type,
                        reasons=reasons,
                        recommendation_text=f"Move {resource_type} into a private subnet and restrict direct internet access.",
                        priority=priority,
                        category="SECURITY",
                        estimated_impact="90% Security Posture Improvement"
                    ))
                elif f_type in ["OPEN_SSH", "SSH_OPEN", "MOCK_PORT_ANALYSIS"]:
                    recommendations.append(Recommendation(
                        issue_title=f"Open Port detected on {resource_type}",
                        resource_id=resource_id,
                        resource_type=resource_type,
                        reasons=[finding.get("description", "Port might be exposed to 0.0.0.0/0")],
                        recommendation_text="Restrict inbound rules to VPN or Bastion Host IPs only.",
                        priority="CRITICAL",
                        category="SECURITY",
                        estimated_impact="High Reduction in Attack Surface"
                    ))
                elif f_type in ["IAM_OVER_PRIVILEGED", "HIGH_PRIVILEGE"]:
                    recommendations.append(Recommendation(
                        issue_title=f"Over-privileged IAM attached to {resource_type}",
                        resource_id=resource_id,
                        resource_type=resource_type,
                        reasons=[finding.get("description", "Resource has excessive permissions")],
                        recommendation_text="Implement Least Privilege Policy. Audit and scope down attached IAM policies.",
                        priority=priority,
                        category="SECURITY",
                        estimated_impact="Prevents blast radius expansion during a breach"
                    ))
                elif f_type == "WAF_MISSING":
                    recommendations.append(Recommendation(
                        issue_title=f"WAF Missing on {resource_type}",
                        resource_id=resource_id,
                        resource_type=resource_type,
                        reasons=["Application Load Balancer has no WAF attached."],
                        recommendation_text="Attach a Web Application Firewall (WAF) to protect against common web exploits.",
                        priority=priority,
                        category="SECURITY",
                        estimated_impact="Protects against OWASP Top 10"
                    ))
                elif f_type == "VPC_ATTACHMENT_MISSING":
                    recommendations.append(Recommendation(
                        issue_title=f"Missing VPC Attachment on {resource_type}",
                        resource_id=resource_id,
                        resource_type=resource_type,
                        reasons=["Lambda is not attached to a VPC."],
                        recommendation_text="Attach Lambda to a VPC to enable secure access to private subnets (e.g. RDS, ElastiCache).",
                        priority="LOW",
                        category="SECURITY",
                        estimated_impact="Enables private backend connectivity"
                    ))
                    
        return recommendations

    def analyze_environment(self) -> List[Recommendation]:
        """
        Scans all critical nodes in the environment and aggregates recommendations.
        """
        all_recs = []
        if not self.neo4j.driver:
            return all_recs
            
        try:
            # Query a sample of key compute and database resources
            query = """
            MATCH (n) WHERE labels(n)[0] IN ['EC2', 'RDS', 'Lambda', 'ALB']
            RETURN n.id AS id
            LIMIT 50
            """
            results = self.neo4j.query(query)
            for res in results:
                recs = self.analyze_resource(res["id"])
                all_recs.extend(recs)
        except Exception as e:
            pass
            
        # Sort by priority
        priority_map = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4, "GOOD": 5}
        all_recs.sort(key=lambda x: priority_map.get(x.priority, 99))
        
        return all_recs
