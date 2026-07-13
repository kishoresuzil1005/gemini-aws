from typing import Dict, Any, List
from app.services.ai.production_checklist import ProductionChecklistService as ProductionChecklist

class ProductionBestPractices:
    def __init__(self):
        self.checklist_generator = ProductionChecklist()

    def evaluate(self, inventory: Dict[str, Any], findings: Dict[str, List[str]], scoring: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates the environment against production-grade standards to generate a 
        Production Readiness Assessment.
        """
        
        # Base points for readiness percentage
        max_points = 50
        points_earned = 50
        
        checklist = {
            "Networking": {"status": "Pass", "items": []},
            "Compute": {"status": "Pass", "items": []},
            "Database": {"status": "Pass", "items": []},
            "Security": {"status": "Pass", "items": []},
            "Monitoring": {"status": "Pass", "items": []},
            "Automation": {"status": "Pass", "items": []}
        }
        
        critical_findings = []
        recommendations = []
        
        # Security
        sec_findings = findings.get("security_findings", [])
        if any("CloudTrail" in f for f in sec_findings):
            critical_findings.append("CloudTrail is not enabled.")
            recommendations.append("Enable CloudTrail for auditability and compliance.")
            checklist["Security"]["status"] = "Fail"
            checklist["Security"]["items"].append("CloudTrail Missing")
            points_earned -= 5
        else:
            checklist["Security"]["items"].append("CloudTrail Enabled")

        # Database / High Availability
        if inventory.get("rds", 0) > 0 and not inventory.get("multi_az_rds", False):
            critical_findings.append("RDS is deployed in a single Availability Zone.")
            recommendations.append("Configure Multi-AZ for production RDS instances.")
            checklist["Database"]["status"] = "Fail"
            checklist["Database"]["items"].append("Single AZ RDS")
            points_earned -= 5
        else:
            checklist["Database"]["items"].append("Multi-AZ Configuration Valid")

        # Compute / Auto Scaling
        if inventory.get("ec2", 0) > 0 and inventory.get("auto_scaling", 0) == 0:
            critical_findings.append("EC2 instances lack Auto Scaling Groups.")
            recommendations.append("Implement Auto Scaling for stateless workloads.")
            checklist["Compute"]["status"] = "Fail"
            checklist["Compute"]["items"].append("Missing ASG")
            points_earned -= 4
        else:
            checklist["Compute"]["items"].append("Compute Scalability Valid")

        # Monitoring
        if inventory.get("cloudwatch", 0) == 0:
            critical_findings.append("CloudWatch monitoring not fully configured.")
            recommendations.append("Configure CloudWatch Alarms and Dashboards.")
            checklist["Monitoring"]["status"] = "Fail"
            checklist["Monitoring"]["items"].append("Missing CloudWatch Alarms")
            points_earned -= 3
        else:
            checklist["Monitoring"]["items"].append("Monitoring Enabled")

        # Calculate Score and Grade
        readiness_score = int((points_earned / max_points) * 100)
        
        if readiness_score >= 90:
            grade = "A"
            production_ready = True
            environment_type = "Production Ready"
        elif readiness_score >= 80:
            grade = "B"
            production_ready = False
            environment_type = "Mostly Production Ready"
        elif readiness_score >= 60:
            grade = "C"
            production_ready = False
            environment_type = "Needs Improvement"
        else:
            grade = "D"
            production_ready = False
            environment_type = "Development Only"
            
        pillar_scores = {
            "networking": 9,
            "security": 10 if checklist["Security"]["status"] == "Pass" else 6,
            "availability": 10 if checklist["Database"]["status"] == "Pass" else 5,
            "automation": 7,
            "monitoring": 10 if checklist["Monitoring"]["status"] == "Pass" else 6
        }
        
        # Generate deep deployment checklist
        detailed_checklist = self.checklist_generator.generate(inventory, findings, scoring)

        return {
            "production_ready": production_ready,
            "readiness_score": readiness_score,
            "grade": grade,
            "environment_type": environment_type,
            "pillar_scores": pillar_scores,
            "critical_findings": critical_findings,
            "recommendations": recommendations,
            "production_checklist": checklist,
            "detailed_checklist": detailed_checklist
        }