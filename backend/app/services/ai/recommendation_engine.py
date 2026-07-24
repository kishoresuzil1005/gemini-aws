from typing import List, Dict, Any
from pydantic import BaseModel
from fastapi import HTTPException
from knowledge.service.client_factory import get_default_client
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
    def __init__(self, knowledge_client=None):
        self.client = knowledge_client or get_default_client()
        self.security_analyzer = SecurityImpactAnalyzer(self.client)
        self.criticality_analyzer = CriticalityAnalyzer(self.client)
        
    def _determine_resource_type(self, resource_id: str) -> str:
        try:
            resource = self.client.get_resource(resource_id)
            if resource and resource.get("type"):
                return resource["type"]
        except Exception:
            pass
        return "Unknown"

    def analyze_resource(self, resource_id: str) -> List[Recommendation]:
        """
        Consumes graph analyses for a specific resource and synthesizes actionable recommendations.
        """
        if not self.client.get_resource(resource_id):
            raise HTTPException(status_code=404, detail="Resource not found")
            
        recommendations = {}
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
                if crit_level == "CRITICAL":
                    if priority in ["HIGH", "MEDIUM"]: priority = "CRITICAL"
                    elif priority == "LOW": priority = "MEDIUM"
                elif crit_level == "HIGH":
                    if priority == "MEDIUM": priority = "HIGH"
                    elif priority == "LOW": priority = "MEDIUM"
                    
                rec = None
                if f_type in ["PUBLIC_ACCESS", "NETWORK_PUBLIC", "PUBLIC_SUBNET", "INTERNET_FACING", "PUBLIC_RDS"]:
                    if resource_type == "RDS" or f_type == "PUBLIC_RDS":
                        rec = Recommendation(
                            issue_title=f"Public Exposure on {resource_type}",
                            resource_id=resource_id,
                            resource_type=resource_type,
                            reasons=reasons,
                            recommendation_text="Disable public accessibility and move into a private subnet.",
                            priority=priority,
                            category="SECURITY",
                            estimated_impact="High Security Posture Improvement"
                        )
                    elif resource_type == "ALB":
                        # ALB Internet-Facing is expected, but WAF/HTTPS are needed, so upgrade to MEDIUM
                        rec_priority = "MEDIUM" if priority in ["INFO", "LOW"] else priority
                        rec = Recommendation(
                            issue_title=f"Public Exposure on {resource_type}",
                            resource_id=resource_id,
                            resource_type=resource_type,
                            reasons=reasons,
                            recommendation_text="Review whether the ALB should be internet-facing and ensure it is protected by WAF and appropriate security groups.",
                            priority=rec_priority,
                            category="SECURITY",
                            estimated_impact="Reduces exposure risk"
                        )
                    else:
                        rec = Recommendation(
                            issue_title=f"Public Exposure on {resource_type}",
                            resource_id=resource_id,
                            resource_type=resource_type,
                            reasons=reasons,
                            recommendation_text=f"Move workload to a private subnet.",
                            priority=priority,
                            category="SECURITY",
                            estimated_impact="90% Security Posture Improvement"
                        )
                elif f_type in ["OPEN_SSH", "SSH_OPEN", "MOCK_PORT_ANALYSIS"]:
                    rec = Recommendation(
                        issue_title=f"Open Port detected on {resource_type}",
                        resource_id=resource_id,
                        resource_type=resource_type,
                        reasons=[finding.get("description", "Port might be exposed to 0.0.0.0/0")],
                        recommendation_text="Restrict SSH access to VPN or Bastion Host IPs only.",
                        priority=priority,
                        category="SECURITY",
                        estimated_impact="High Reduction in Attack Surface"
                    )
                elif f_type in ["IAM_OVER_PRIVILEGED", "HIGH_PRIVILEGE"]:
                    rec = Recommendation(
                        issue_title=f"Over-privileged IAM attached to {resource_type}",
                        resource_id=resource_id,
                        resource_type=resource_type,
                        reasons=[finding.get("description", "Resource has excessive permissions")],
                        recommendation_text="Apply least privilege policy. Audit and scope down attached IAM policies.",
                        priority=priority,
                        category="SECURITY",
                        estimated_impact="Prevents blast radius expansion during a breach"
                    )
                elif f_type == "WAF_MISSING":
                    rec = Recommendation(
                        issue_title=f"WAF Missing on {resource_type}",
                        resource_id=resource_id,
                        resource_type=resource_type,
                        reasons=["Application Load Balancer has no WAF attached."],
                        recommendation_text="Attach AWS WAF to protect against common web exploits.",
                        priority=priority,
                        category="SECURITY",
                        estimated_impact="Protects against OWASP Top 10"
                    )
                elif f_type == "VPC_ATTACHMENT_MISSING":
                    rec = Recommendation(
                        issue_title=f"Missing VPC Attachment on {resource_type}",
                        resource_id=resource_id,
                        resource_type=resource_type,
                        reasons=["Lambda is not attached to a VPC."],
                        recommendation_text="Attach Lambda to a VPC.",
                        priority=priority,
                        category="SECURITY",
                        estimated_impact="Enables private backend connectivity"
                    )
                
                # Add GOOD findings for informational purposes so that EC2/RDS still return info if safe
                if not rec and severity == "GOOD":
                    rec = Recommendation(
                        issue_title=f"Secure Configuration on {resource_type}",
                        resource_id=resource_id,
                        resource_type=resource_type,
                        reasons=[finding.get("description", "Resource is securely configured.")],
                        recommendation_text="Maintain current security posture.",
                        priority="INFO",
                        category="SECURITY",
                        estimated_impact="Maintains Security Posture"
                    )

                if rec and rec.issue_title not in recommendations:
                    recommendations[rec.issue_title] = rec

        return list(recommendations.values())

    def analyze_environment(self) -> List[Recommendation]:
        """
        Scans all critical nodes in the environment and aggregates recommendations.
        """
        all_recs = []
            
        try:
            # Query a sample of key compute and database resources
            query = """
            MATCH (n) WHERE labels(n)[0] IN ['EC2', 'RDS', 'Lambda', 'ALB']
            RETURN n.id AS id
            LIMIT 50
            """
            try:
                results = self.client.query_graph(query)
                for res in results:
                    recs = self.analyze_resource(res.get("id"))
                    all_recs.extend(recs)
            except NotImplementedError:
                pass
        except Exception as e:
            pass
            
        # Sort by priority
        priority_map = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4, "GOOD": 5}
        
        # Deduplicate globally and filter INFO/GOOD
        unique_recs = {}
        for r in all_recs:
            if r.priority in ["INFO", "GOOD"]:
                continue
            key = f"{r.resource_id}-{r.issue_title}"
            if key not in unique_recs:
                unique_recs[key] = r
                
        final_list = list(unique_recs.values())
        final_list.sort(key=lambda x: priority_map.get(x.priority, 99))
        
        return final_list