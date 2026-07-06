import logging
from fastapi import HTTPException
from app.services.graph.neo4j_service import Neo4jService
from app.services.graph.analysis.security.exposure_analyzer import ExposureAnalyzer
from app.services.graph.analysis.security.security_group_analyzer import SecurityGroupAnalyzer
from app.services.graph.analysis.security.iam_analyzer import IAMAnalyzer
from app.services.graph.analysis.security.network_analyzer import NetworkAnalyzer
from app.services.graph.analysis.security.attack_path_analyzer import AttackPathAnalyzer
from app.services.graph.analysis.security.recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)

class SecurityImpactAnalyzer:
    def __init__(self, neo4j_service: Neo4jService = None):
        self.neo4j = neo4j_service or Neo4jService()
        self.exposure_analyzer = ExposureAnalyzer(self.neo4j)
        self.sg_analyzer = SecurityGroupAnalyzer(self.neo4j)
        self.iam_analyzer = IAMAnalyzer(self.neo4j)
        self.network_analyzer = NetworkAnalyzer(self.neo4j)
        self.attack_path_analyzer = AttackPathAnalyzer(self.neo4j)
        self.recommendation_engine = RecommendationEngine()

    def analyze(self, resource_id: str):
        """
        Orchestrates an end-to-end security analysis for a single resource.
        """
        if not self.neo4j.node_exists(resource_id):
            raise HTTPException(status_code=404, detail="Resource not found")
            
        findings = []
        
        # 1. Check Network Exposure
        exposure_result = self.exposure_analyzer.analyze(resource_id)
        if exposure_result.get("internet_accessible"):
            findings.append({
                "type": "PUBLIC_ACCESS",
                "severity": "HIGH",
                "description": "Instance is reachable from the Internet"
            })
            
        # 2. Check Attack Paths
        attack_result = self.attack_path_analyzer.analyze(resource_id)
        if attack_result.get("paths"):
            findings.append({
                "type": "ATTACK_PATH_DETECTED",
                "severity": attack_result.get("risk_level", "HIGH"),
                "description": f"Found {len(attack_result['paths'])} downstream paths to sensitive data."
            })
            
        # Overall risk
        risk = "LOW"
        if any(f["severity"] == "CRITICAL" for f in findings):
            risk = "CRITICAL"
        elif any(f["severity"] == "HIGH" for f in findings):
            risk = "HIGH"
        elif any(f["severity"] == "MEDIUM" for f in findings):
            risk = "MEDIUM"
            
        recommendations = self.recommendation_engine.generate(findings)
        
        return {
            "resource": resource_id,
            "risk": risk,
            "findings": findings,
            "recommendations": recommendations,
            "exposure_details": exposure_result,
            "attack_paths": attack_result.get("paths", [])
        }
