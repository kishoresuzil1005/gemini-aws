import json
from typing import Dict, Any, List
from app.services.ai.architecture_patterns import ArchitecturePatterns

class ArchitectureService:
    def __init__(self):
        self.WORKLOADS = {
            "web_application": ["web", "website", "frontend", "backend", "three tier", "3 tier", "web app"],
            "serverless": ["lambda", "serverless", "api gateway"],
            "kubernetes": ["eks", "kubernetes", "pods", "k8s"],
            "microservices": ["microservices", "service mesh", "ecs"],
            "data_platform": ["athena", "redshift", "glue", "emr"]
        }
        
        self.PATTERNS = {
            "three_tier": ["three tier", "3 tier"],
            "high_availability": ["high availability", "ha", "highly available"],
            "microservices": ["microservices"],
            "serverless": ["serverless"],
            "event_driven": ["event driven", "sqs", "sns", "eventbridge"]
        }
        
        self.SERVICE_KEYWORDS = {
            "Route53": ["route53", "dns"],
            "CloudFront": ["cloudfront", "cdn"],
            "ALB": ["alb", "load balancer", "elb", "nlb"],
            "EC2": ["ec2", "instance", "server", "vm"],
            "RDS": ["rds", "mysql", "postgres", "database", "aurora"],
            "Lambda": ["lambda", "function"],
            "API Gateway": ["api gateway", "apigw"],
            "S3": ["s3", "bucket", "object storage"],
            "EKS": ["eks", "kubernetes"],
            "ECS": ["ecs", "fargate"],
            "VPC": ["vpc", "subnet", "network"],
            "IAM": ["iam", "role", "policy"],
            "CloudWatch": ["cloudwatch", "monitoring", "logs"]
        }
        
        self.REQUIREMENTS = {
            "high_availability": ["high availability", "ha", "highly available", "multi-az", "fault tolerant"],
            "security": ["secure", "security", "encryption", "iam", "kms", "waf", "guardduty"],
            "monitoring": ["monitor", "monitoring", "observability", "cloudwatch", "logs", "metrics"],
            "backup": ["backup", "snapshot"],
            "cost_optimized": ["cost", "cheap", "optimize", "savings", "budget"],
            "production": ["production", "prod", "enterprise"],
            "dr": ["disaster recovery", "dr", "failover", "multi region"]
        }

        # Try to import graph and criticality services
        try:
            from app.services.graph.neo4j_service import Neo4jService
            from app.services.graph.criticality_service import CriticalityService
            self.neo4j = Neo4jService()
            self.criticality = CriticalityService()
            self.has_graph_services = True
        except ImportError:
            self.has_graph_services = False
            
        self.pattern_library = ArchitecturePatterns()

    def analyze(self, query: str) -> Dict[str, Any]:
        query_lower = query.lower()
        
        # 1. Detect Workload
        detected_workload = "unknown"
        for wl, keywords in self.WORKLOADS.items():
            if any(kw in query_lower for kw in keywords):
                detected_workload = wl
                break
                
        # 2. Detect Pattern
        detected_pattern = "standard"
        for pat, keywords in self.PATTERNS.items():
            if any(kw in query_lower for kw in keywords):
                detected_pattern = pat
                break
                
        # 3. Detect Services
        detected_services = set()
        for svc, keywords in self.SERVICE_KEYWORDS.items():
            if any(kw in query_lower for kw in keywords):
                detected_services.add(svc)
                
        # Implied services based on workload
        if detected_workload == "web_application" or detected_pattern == "three_tier":
            detected_services.update(["Route53", "CloudFront", "ALB", "EC2", "RDS", "S3", "VPC", "IAM"])
        elif detected_workload == "kubernetes":
            detected_services.update(["EKS", "ALB", "VPC", "IAM", "CloudWatch"])
            
        # 4. Detect Requirements
        detected_requirements = {
            "high_availability": False,
            "security": False,
            "monitoring": False,
            "backup": False,
            "cost_optimized": False,
            "production": False,
            "dr": False
        }
        for req, keywords in self.REQUIREMENTS.items():
            if any(kw in query_lower for kw in keywords):
                detected_requirements[req] = True
                
        # 5. Build Graph and Criticality Context (If applicable)
        graph_context = {}
        criticality_context = {}
        inventory_context = {}
        
        if self.has_graph_services and ("review" in query_lower or "fails" in query_lower or "critical" in query_lower):
            # Very basic extraction of resource ID for demonstration 
            # (e.g. "What happens if cloudops-db fails?")
            words = query_lower.split()
            resource_id = None
            for w in words:
                if w.startswith("cloudops-") or "db" in w or "vpc-" in w or "i-" in w:
                    resource_id = w.strip("?")
                    break
                    
            if resource_id:
                try:
                    # Attempt to get graph relations
                    rels = self.neo4j.get_relationships(resource_id)
                    if rels:
                        graph_context["dependencies"] = rels
                    
                    # Attempt to get criticality
                    crit = self.criticality.calculate(resource_id)
                    if crit:
                        criticality_context = crit
                except Exception as e:
                    print(f"[ArchitectureService] Error fetching graph/criticality context: {e}")
            
            # Simple mock inventory signal for "review my architecture"
            if "review" in query_lower and "architecture" in query_lower:
                inventory_context["signal"] = "fetch_full_inventory"

        return {
            "mode": "architecture",
            "workload": detected_workload,
            "pattern": detected_pattern,
            "architecture_pattern": self.pattern_library.get_pattern(detected_workload),
            "deployment": "ec2" if "ec2" in detected_services else "managed",
            "services": list(detected_services),
            "requirements": detected_requirements,
            "graph_context": graph_context,
            "inventory_context": inventory_context,
            "criticality_context": criticality_context
        }
