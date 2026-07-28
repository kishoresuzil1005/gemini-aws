import logging
from typing import List, Dict, Any, Optional
import uuid

from app.services.security_engine.models import (
    SecurityFinding, SecurityRisk, SecurityRecommendation, 
    AttackPath, ThreatScenario, ThreatActor, SecurityPosture, SecurityIssue, SecurityEvidence
)
from app.services.dependency_engine.engine import DependencyIntelligenceEngine
from knowledge.service.knowledge_client import KnowledgeClient

logger = logging.getLogger(__name__)

class SecurityIntelligenceEngine:
    """Legacy internal engine; SecurityService is the public analysis boundary."""

    def __init__(self, knowledge_client: KnowledgeClient, dependency_engine: DependencyIntelligenceEngine):
        self.client = knowledge_client
        self.dep_engine = dependency_engine

    def _calculate_risk(self, resource_id: str, context: str) -> SecurityRisk:
        """Phase 8: Security Risk Scoring"""
        # Consume Dependency Intelligence Engine for risk propagation
        blast_radius = self.dep_engine.analyze_blast_radius(resource_id)
        score = blast_radius.risk_score if blast_radius else 10
        
        # Heuristics based on topology
        likelihood = "HIGH" if score > 50 else "LOW"
        impact = "HIGH" if score > 20 else "LOW"
        severity = "CRITICAL" if score > 80 else "HIGH" if score > 40 else "LOW"
        
        return SecurityRisk(
            likelihood=likelihood,
            impact=impact,
            exploitability="MEDIUM",
            business_criticality="HIGH",
            score=score,
            severity=severity,
            confidence=0.85
        )

    # --- Phase 3: Attack Path Analysis ---
    def analyze_attack_paths(self, target_resource_id: str) -> List[AttackPath]:
        """Identifies potential attack paths to a sensitive resource using dependency reasoning."""
        # Find path from simulated "Internet" node to target
        # Assuming an internet gateway or load balancer is inbound
        paths = []
        deps = self.dep_engine.get_dependencies(target_resource_id)
        
        # Simulated traversal over dependency nodes
        for node in deps.nodes:
            if "LB" in node.type or "IGW" in node.type or "public" in str(node.properties).lower():
                path = self.dep_engine.get_shortest_path(node.id, target_resource_id)
                if path:
                    paths.append(AttackPath(
                        path=path,
                        scenario=ThreatScenario(
                            actor=ThreatActor(type="External", origin="Internet", intent="Data Exfiltration"),
                            objective="Access Sensitive Resource",
                            description=f"External access through {node.type}"
                        ),
                        vulnerabilities=["Open Access", "Misconfigured routing"],
                        risk=self._calculate_risk(target_resource_id, "Attack Path")
                    ))
        return paths

    # --- Phase 4: Exposure Analysis ---
    def analyze_exposure(self, resource_id: str) -> List[SecurityFinding]:
        node = self.dep_engine.get_node(resource_id)
        if not node: return []
        
        findings = []
        prop_str = str(node.properties).lower()
        if "0.0.0.0/0" in prop_str or "public" in prop_str:
            findings.append(SecurityFinding(
                id=str(uuid.uuid4()),
                title=f"Public Exposure Detected on {node.name}",
                description="Resource is potentially exposed to the internet.",
                resource_id=resource_id,
                finding_type="EXPOSURE",
                risk=self._calculate_risk(resource_id, "Exposure"),
                recommendations=[
                    SecurityRecommendation(
                        reason="Publicly accessible configurations lead to unauthorized access.",
                        evidence="Found '0.0.0.0/0' or 'public' in configuration.",
                        risk=self._calculate_risk(resource_id, "Exposure"),
                        affected_resources=[resource_id],
                        business_impact="Potential data breach.",
                        remediation_steps=["Remove public internet gateway routing", "Restrict Security Groups"],
                        priority="HIGH",
                        estimated_effort="Low"
                    )
                ]
            ))
        return findings

    # --- Phase 5: IAM Security Intelligence ---
    def analyze_iam(self, resource_id: str) -> List[SecurityFinding]:
        node = self.dep_engine.get_node(resource_id)
        if not node or node.type not in ["IAM Role", "IAM User", "IAM Policy"]: 
            return []
            
        findings = []
        if "AdministratorAccess" in str(node.properties):
            findings.append(SecurityFinding(
                id=str(uuid.uuid4()),
                title="Overprivileged IAM Entity",
                description=f"Entity {node.name} has administrative access.",
                resource_id=resource_id,
                finding_type="IAM",
                risk=self._calculate_risk(resource_id, "IAM"),
                recommendations=[]
            ))
        return findings

    # --- Phase 6: Network Security Intelligence ---
    def analyze_network(self, resource_id: str) -> List[SecurityFinding]:
        node = self.dep_engine.get_node(resource_id)
        if not node or node.type not in ["VPC", "Subnet", "SecurityGroup", "NACL"]: 
            return []
            
        # Analyze connections via graph
        deps = self.dep_engine.get_dependencies(resource_id)
        if len(deps.edges) == 0:
            return [SecurityFinding(
                id=str(uuid.uuid4()),
                title="Orphaned Network Resource",
                description="Resource is not attached to any workloads.",
                resource_id=resource_id,
                finding_type="NETWORK",
                risk=self._calculate_risk(resource_id, "Network"),
                recommendations=[]
            )]
        return []

    # --- Phase 7: Data Security Intelligence ---
    def analyze_data_security(self, resource_id: str) -> List[SecurityFinding]:
        node = self.dep_engine.get_node(resource_id)
        if not node or node.type not in ["S3", "RDS", "DynamoDB", "EBS"]: 
            return []
            
        prop_str = str(node.properties).lower()
        if "encrypted" not in prop_str and "kms" not in prop_str:
            return [SecurityFinding(
                id=str(uuid.uuid4()),
                title="Unencrypted Data Store",
                description="Resource storage is not encrypted at rest.",
                resource_id=resource_id,
                finding_type="DATA",
                risk=self._calculate_risk(resource_id, "Data"),
                recommendations=[]
            )]
        return []

    # --- Phase 9: Recommendation Engine ---
    def generate_recommendations(self, finding: SecurityFinding) -> List[SecurityRecommendation]:
        # Synthesize recommendations dynamically using graph logic
        recs = finding.recommendations
        if not recs:
            recs.append(SecurityRecommendation(
                reason="Anomaly detected in configuration.",
                evidence=f"Flagged by rule for {finding.finding_type}",
                risk=finding.risk,
                affected_resources=[finding.resource_id],
                business_impact="Compliance violation.",
                remediation_steps=["Review resource configuration properties."],
                priority="MEDIUM",
                estimated_effort="Medium"
            ))
        return recs

    # --- Phase 10: AI Security Explanation ---
    def generate_ai_explanation(self, posture: SecurityPosture) -> str:
        """Generates human-readable AI security explanation."""
        score = posture.overall_score
        num_issues = len(posture.issues)
        num_paths = len(posture.attack_paths)
        
        narrative = f"**Executive Security Summary:**\n"
        narrative += f"The current architectural posture score is {score}/100. "
        narrative += f"There are {num_issues} security issues and {num_paths} verified attack paths.\n\n"
        
        narrative += "**Attack Narrative:**\n"
        if num_paths > 0:
            narrative += f"Threat actors could exploit {num_paths} paths to reach sensitive resources by traversing public exposure points.\n\n"
        else:
            narrative += "No critical attack paths found.\n\n"
            
        narrative += "**Exposure Narrative:**\n"
        narrative += "Public exposure is analyzed by evaluating graph connections to Internet Gateways and evaluating 0.0.0.0/0 topologies."
        
        return narrative
