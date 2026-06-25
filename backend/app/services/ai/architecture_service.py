import json
from typing import Dict, Any, List
from app.services.ai.architecture_patterns import ArchitecturePatterns
from app.services.ai.architecture_review import ArchitectureReview
from app.services.ai.failure_analysis import FailureAnalysis
from app.services.ai.production_best_practices import ProductionBestPractices

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
        self.architecture_review = ArchitectureReview()
        self.failure_analysis = FailureAnalysis()
        self.production_reviewer = ProductionBestPractices()

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
                
        # 6. Architecture Review Trigger
        review_context = {}
        if "review" in query_lower or "analyze" in query_lower and "fail" not in query_lower:
            review_context = self.architecture_review.review()
            
        # 7. Failure Analysis Trigger
        failure_context = {}
        if "fail" in query_lower or "blast radius" in query_lower:
            # Simple heuristic to grab the resource name from "what happens if X fails"
            words = query_lower.split()
            resource_name = "unknown-resource"
            for i, word in enumerate(words):
                if word in ["if", "of", "radius", "for"]:
                    if i + 1 < len(words) and words[i+1] not in ["the", "my", "a"]:
                        resource_name = words[i+1]
                        break
                    elif i + 2 < len(words):
                        resource_name = words[i+2]
                        break
            # Fallback if the user specifically asked about cloudops-db
            if "cloudops-db" in query_lower:
                resource_name = "cloudops-db"
                
            failure_context = self.failure_analysis.analyze(resource_name)
            
        # 8. Production Readiness Trigger
        production_context = {}
        if "production" in query_lower or "best practice" in query_lower or "checklist" in query_lower:
            # We need review findings and score data for production eval.
            # If review wasn't triggered explicitly, we run a background review now.
            if not review_context:
                review_context = self.architecture_review.review()
            
            # The architecture_review.review() returns 'scoring' within its dictionary.
            score_data = review_context.get("scoring", {})
            findings_dict = {
                "security_findings": review_context.get("security_findings", []),
                "network_findings": review_context.get("network_findings", []),
                "reliability_findings": review_context.get("reliability_findings", []),
                "cost_findings": review_context.get("cost_findings", []),
                "monitoring_findings": review_context.get("monitoring_findings", [])
            }
            production_context = self.production_reviewer.evaluate(inventory_context, findings_dict, score_data)

        return {
            "mode": "architecture",
            "workload": detected_workload,
            "pattern": detected_pattern,
            "architecture_pattern": self.pattern_library.get_pattern(detected_workload),
            "deployment": "ec2" if "ec2" in detected_services else "managed",
            "services": list(detected_services),
            "requirements": detected_requirements,
            "graph_context": graph_context,
            "cost_findings": review_context.get("cost_findings", []), # Keeping backward compatibility in context structure
            "review_context": review_context,
            "failure_context": failure_context,
            "production_context": production_context
        }
