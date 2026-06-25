from typing import Dict, Any, List

class ArchitectureScorer:
    def __init__(self):
        self.weights = {
            "availability": 0.20,
            "security": 0.20,
            "reliability": 0.15,
            "performance": 0.15,
            "cost": 0.15,
            "operational_excellence": 0.10,
            "sustainability": 0.05
        }

    def score(self, inventory: Dict[str, Any], findings: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Calculates scores for the 7 pillars based on inventory and findings.
        """
        
        # Base scores
        scores = {
            "availability": 10,
            "security": 10,
            "reliability": 10,
            "performance": 10,
            "cost": 10,
            "operational_excellence": 10,
            "sustainability": 10
        }
        
        recommendations = []
        
        # Evaluate Availability
        if inventory.get("ec2", 0) > 0 and inventory.get("auto_scaling", 0) == 0:
            scores["availability"] -= 3
            recommendations.append("Create Auto Scaling Group.")
        if inventory.get("rds", 0) > 0 and not inventory.get("multi_az_rds", False):
            scores["availability"] -= 2
            recommendations.append("Enable Multi AZ for RDS.")
            
        # Evaluate Security
        sec_findings = findings.get("security_findings", [])
        if any("CloudTrail" in f for f in sec_findings):
            scores["security"] -= 2
            recommendations.append("Enable CloudTrail.")
        if any("S3" in f and "encryption" in f.lower() for f in sec_findings):
            scores["security"] -= 2
            recommendations.append("Enable S3 Default Encryption.")
        if any("Security Group" in f for f in findings.get("network_findings", [])):
            scores["security"] -= 2
            recommendations.append("Restrict open Security Groups.")
            
        # Evaluate Reliability
        rel_findings = findings.get("reliability_findings", [])
        if any("Auto Scaling" in f for f in rel_findings):
            scores["reliability"] -= 2
        if inventory.get("backup_plans", 0) == 0:
            scores["reliability"] -= 2
            recommendations.append("Configure AWS Backup.")
            
        # Evaluate Performance
        if inventory.get("cloudfront", 0) == 0 and inventory.get("s3", 0) > 0:
            scores["performance"] -= 1
            recommendations.append("Consider CloudFront for S3 assets.")
            
        # Evaluate Cost
        cost_findings = findings.get("cost_findings", [])
        if any("idle" in f.lower() for f in cost_findings):
            scores["cost"] -= 2
            recommendations.append("Rightsize or terminate idle EC2 instances.")
        if any("EBS" in f for f in cost_findings):
            scores["cost"] -= 1
            recommendations.append("Delete unused EBS volumes.")
            
        # Evaluate Operational Excellence
        mon_findings = findings.get("monitoring_findings", [])
        if any("CloudWatch" in f for f in mon_findings):
            scores["operational_excellence"] -= 2
            recommendations.append("Configure CloudWatch Alarms.")
            
        # Evaluate Sustainability
        if inventory.get("ec2", 0) > 0 and inventory.get("spot_instances", 0) == 0:
            scores["sustainability"] -= 1
            recommendations.append("Explore Spot Instances for fault-tolerant workloads.")
            
        # Clamp scores to 0-10
        for pillar in scores:
            scores[pillar] = max(0, min(10, scores[pillar]))

        # Calculate weighted overall score
        overall_score = sum(scores[pillar] * (self.weights[pillar] * 10) for pillar in scores)
        overall_score = round(overall_score)
        
        # Calculate grade
        if overall_score >= 95:
            grade = "A+"
        elif overall_score >= 90:
            grade = "A"
        elif overall_score >= 80:
            grade = "B"
        elif overall_score >= 70:
            grade = "C"
        elif overall_score >= 60:
            grade = "D"
        else:
            grade = "F"
            
        return {
            "overall_score": overall_score,
            "grade": grade,
            "pillar_scores": scores,
            "recommendations": list(set(recommendations))
        }
