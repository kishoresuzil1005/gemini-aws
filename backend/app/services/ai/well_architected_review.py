from typing import Dict, Any, List

class WellArchitectedReview:
    def __init__(self):
        pass

    def generate(self, inventory: Dict[str, Any], graph: Dict[str, Any], review_findings: Dict[str, List[str]], scoring: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a structured AWS Well-Architected Framework review.
        """
        
        pillar_scores = scoring.get("pillar_scores", {})
        
        # 1. Operational Excellence
        op_strengths = []
        op_weaknesses = []
        op_recs = []
        
        if inventory.get("cloudwatch", 1) > 0:
            op_strengths.append("CloudWatch monitoring detected.")
        else:
            op_weaknesses.append("CloudWatch missing or underutilized.")
            op_recs.append("Configure CloudWatch Dashboards and Alarms.")
            
        if any("CloudTrail" in f for f in review_findings.get("security_findings", [])):
            op_weaknesses.append("CloudTrail not fully configured.")
            op_recs.append("Enable CloudTrail across all regions.")
            
        # 2. Security
        sec_strengths = []
        sec_weaknesses = []
        sec_recs = []
        
        if inventory.get("iam_roles", 1) > 0:
            sec_strengths.append("IAM Roles deployed.")
            
        if any("S3" in f for f in review_findings.get("security_findings", [])):
            sec_weaknesses.append("S3 bucket encryption gaps detected.")
            sec_recs.append("Enable default S3 KMS encryption.")
            
        if any("Security Group" in f for f in review_findings.get("network_findings", [])):
            sec_weaknesses.append("Overly permissive Security Groups.")
            sec_recs.append("Restrict Security Group ingress to required ports only.")
            
        # 3. Reliability
        rel_strengths = []
        rel_weaknesses = []
        rel_recs = []
        
        if inventory.get("rds", 0) > 0:
            rel_strengths.append("Relational Database Service (RDS) in use.")
            
        if any("Multi-AZ" in f for f in review_findings.get("spofs", [])):
            rel_weaknesses.append("Single-AZ RDS detected.")
            rel_recs.append("Configure Multi-AZ for production RDS instances.")
            
        if any("Auto Scaling" in f for f in review_findings.get("reliability_findings", [])):
            rel_weaknesses.append("Missing Auto Scaling Groups for EC2.")
            rel_recs.append("Place stateless EC2 workloads behind an Auto Scaling Group.")
            
        # 4. Performance Efficiency
        perf_strengths = []
        perf_weaknesses = []
        perf_recs = []
        
        if inventory.get("alb", 1) > 0:
            perf_strengths.append("Application Load Balancer deployed.")
            
        if inventory.get("cloudfront", 0) == 0:
            perf_weaknesses.append("CloudFront CDN not detected.")
            perf_recs.append("Use CloudFront to cache static assets globally.")
            
        # 5. Cost Optimization
        cost_strengths = []
        cost_weaknesses = []
        cost_recs = []
        
        if inventory.get("cost_explorer", 1) > 0:
            cost_strengths.append("Cost Explorer enabled.")
            
        for f in review_findings.get("cost_findings", []):
            cost_weaknesses.append(f)
            if "idle" in f.lower():
                cost_recs.append("Rightsize or terminate idle EC2 instances.")
            if "ebs" in f.lower():
                cost_recs.append("Delete unattached EBS volumes.")
                
        # 6. Sustainability
        sus_strengths = []
        sus_weaknesses = []
        sus_recs = []
        
        if inventory.get("auto_scaling", 0) > 0:
            sus_strengths.append("Auto Scaling reduces idle energy waste.")
            
        if inventory.get("spot_instances", 0) == 0:
            sus_weaknesses.append("Spot Instances not utilized.")
            sus_recs.append("Adopt Spot Instances for fault-tolerant workloads to improve efficiency.")

        return {
            "operational_excellence": {
                "score": pillar_scores.get("operational_excellence", 10),
                "strengths": op_strengths,
                "weaknesses": op_weaknesses,
                "recommendations": op_recs
            },
            "security": {
                "score": pillar_scores.get("security", 10),
                "strengths": sec_strengths,
                "weaknesses": sec_weaknesses,
                "recommendations": sec_recs
            },
            "reliability": {
                "score": pillar_scores.get("reliability", 10),
                "strengths": rel_strengths,
                "weaknesses": rel_weaknesses,
                "recommendations": rel_recs
            },
            "performance_efficiency": {
                "score": pillar_scores.get("performance", 10),
                "strengths": perf_strengths,
                "weaknesses": perf_weaknesses,
                "recommendations": perf_recs
            },
            "cost_optimization": {
                "score": pillar_scores.get("cost", 10),
                "strengths": cost_strengths,
                "weaknesses": cost_weaknesses,
                "recommendations": cost_recs
            },
            "sustainability": {
                "score": pillar_scores.get("sustainability", 10),
                "strengths": sus_strengths,
                "weaknesses": sus_weaknesses,
                "recommendations": sus_recs
            }
        }
