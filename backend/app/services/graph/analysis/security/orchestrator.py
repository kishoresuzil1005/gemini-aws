import logging
from fastapi import HTTPException
from knowledge.service.client_factory import get_default_client
from app.services.graph.analysis.security.exposure_analyzer import ExposureAnalyzer
from app.services.graph.analysis.security.security_group_analyzer import SecurityGroupAnalyzer
from app.services.graph.analysis.security.iam_analyzer import IAMAnalyzer
from app.services.graph.analysis.security.network_analyzer import NetworkAnalyzer
from app.services.graph.analysis.security.attack_path_analyzer import AttackPathAnalyzer
from app.services.graph.analysis.security.recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)

class SecurityImpactAnalyzer:
    def __init__(self, knowledge_client=None):
        self.client = knowledge_client or get_default_client()
        self.exposure_analyzer = ExposureAnalyzer(self.client)
        self.sg_analyzer = SecurityGroupAnalyzer(self.client)
        self.iam_analyzer = IAMAnalyzer(self.client)
        self.network_analyzer = NetworkAnalyzer(self.client)
        self.attack_path_analyzer = AttackPathAnalyzer(self.client)
        self.recommendation_engine = RecommendationEngine()

    def analyze(self, resource_id: str):
        """
        Orchestrates an end-to-end security analysis for a single resource.
        """
        resource = self.client.get_resource(resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
            
        resource_type = resource.get("type", "Resource")
                
        findings = []
        
        exposure_result = self.exposure_analyzer.analyze(resource_id)
        is_public = exposure_result.get("internet_accessible", False)
        
        # 1. Branching by Resource Type
        if resource_type == "EC2":
            if is_public:
                findings.append({"type": "PUBLIC_SUBNET", "severity": "HIGH", "description": "EC2 instance is in a public subnet."})
                findings.append({"type": "SSH_OPEN", "severity": "CRITICAL", "description": "Port 22 might be exposed to the Internet."})
            else:
                findings.append({"type": "PRIVATE_SUBNET", "severity": "GOOD", "description": "EC2 instance is isolated."})
                
        elif resource_type == "RDS":
            if is_public:
                findings.append({"type": "PUBLIC_SUBNET", "severity": "CRITICAL", "description": "Database is publicly accessible."})
            else:
                findings.append({"type": "PRIVATE_SUBNET", "severity": "GOOD", "description": "Database is correctly placed in a private subnet."})
                findings.append({"type": "NO_PUBLIC_IP", "severity": "GOOD", "description": "Database does not have a public IP attached."})
                
        elif resource_type == "Lambda":
            findings.append({"type": "IAM_OVER_PRIVILEGED", "severity": "MEDIUM", "description": "Lambda function might have excessive permissions."})
            
            # Use exposure_result reasons to determine VPC attachment
            reasons_str = " ".join(exposure_result.get("reason", []))
            if "No VPC attachment" in reasons_str:
                findings.append({"type": "VPC_ATTACHMENT_MISSING", "severity": "LOW", "description": "Lambda is not attached to a VPC."})
            
        elif resource_type == "ALB":
            if is_public:
                findings.append({"type": "INTERNET_FACING", "severity": "INFO", "description": "Application Load Balancer is internet-facing."})
            else:
                findings.append({"type": "INTERNAL_ALB", "severity": "GOOD", "description": "ALB is internal only."})
            findings.append({"type": "WAF_MISSING", "severity": "MEDIUM", "description": "No Web Application Firewall (WAF) attached to ALB."})
            
        elif resource_type == "SecurityGroup":
            sg_results = self.sg_analyzer.analyze(resource_id)
            findings.extend(sg_results.get("findings", []))
            
        else:
            if is_public:
                findings.append({"type": "PUBLIC_ACCESS", "severity": "HIGH", "description": f"{resource_type} is reachable from the Internet"})
                
        # 2. Check Attack Paths (Universal)
        attack_result = self.attack_path_analyzer.analyze(resource_id)
        if attack_result.get("paths") and resource_type not in ["RDS"]:
            findings.append({
                "type": "ATTACK_PATH_DETECTED",
                "severity": attack_result.get("risk_level", "HIGH"),
                "description": f"Found {len(attack_result['paths'])} downstream paths from this {resource_type} to sensitive data."
            })
            
        # Overall risk
        risk = "LOW"
        if any(f["severity"] == "CRITICAL" for f in findings):
            risk = "CRITICAL"
        elif any(f["severity"] == "HIGH" for f in findings):
            risk = "HIGH"
        elif any(f["severity"] == "MEDIUM" for f in findings):
            risk = "MEDIUM"
        elif all(f["severity"] in ["GOOD", "INFO", "LOW"] for f in findings) and findings:
            risk = "GOOD" if any(f["severity"] == "GOOD" for f in findings) else "LOW"
            
        recommendations = self.recommendation_engine.generate(findings)
        
        return {
            "resource": resource_id,
            "risk": risk,
            "internet_accessible": is_public,
            "reason": exposure_result.get("reason", []),
            "findings": findings,
            "recommendations": recommendations,
            "attack_paths": attack_result.get("paths", [])
        }