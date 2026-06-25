from typing import Dict, Any, List

class ArchitectureRecommendation:
    def __init__(self):
        pass

    def generate(self, inventory: Dict[str, Any], review_findings: Dict[str, List[str]], scoring: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates actionable, prioritized recommendations based on the current architecture state.
        """
        recommendations = []
        
        # 1. High Availability Recommendations
        if inventory.get("ec2", 0) > 0 and inventory.get("auto_scaling", 0) == 0:
            recommendations.append({
                "id": "REC-001",
                "category": "High Availability",
                "priority": "HIGH",
                "title": "Deploy EC2 behind an Auto Scaling Group",
                "current_state": "Single EC2 instance handling traffic directly.",
                "recommended_state": "EC2 instances managed by an Auto Scaling Group behind an Application Load Balancer across multiple AZs.",
                "reason": "Single EC2 is a Single Point of Failure (SPOF).",
                "business_impact": "Improves availability and resilience during failures. Reduces downtime.",
                "implementation_effort": "Medium",
                "estimated_availability_impact": "+25%",
                "aws_services": ["ALB", "Auto Scaling", "EC2", "CloudWatch"],
                "implementation_steps": [
                    "Create Launch Template with the current EC2 AMI.",
                    "Create an Auto Scaling Group spanning multiple Availability Zones.",
                    "Attach an Application Load Balancer to the ASG.",
                    "Configure Health Checks."
                ]
            })
            
        if inventory.get("rds", 0) > 0 and not inventory.get("multi_az_rds", False):
            recommendations.append({
                "id": "REC-002",
                "category": "Reliability",
                "priority": "HIGH",
                "title": "Enable Multi-AZ for RDS",
                "current_state": "Single-AZ RDS.",
                "recommended_state": "Multi-AZ RDS with synchronous replication.",
                "reason": "Single-AZ database is a SPOF and risks data loss during AZ failures.",
                "business_impact": "Ensures database high availability and automated failover.",
                "implementation_effort": "Low",
                "estimated_availability_impact": "+20%",
                "aws_services": ["RDS", "CloudWatch"],
                "implementation_steps": [
                    "Modify RDS instance.",
                    "Select 'Create a standby instance'.",
                    "Apply changes during maintenance window."
                ]
            })
            
        # 2. Security Recommendations
        sec_findings = review_findings.get("security_findings", [])
        if any("CloudTrail" in f for f in sec_findings):
            recommendations.append({
                "id": "REC-003",
                "category": "Security",
                "priority": "CRITICAL",
                "title": "Enable CloudTrail across all regions",
                "current_state": "No global API logging.",
                "recommended_state": "CloudTrail enabled globally with logs stored in a secure S3 bucket.",
                "reason": "Missing audit logs prevents incident response and violates compliance.",
                "business_impact": "Enables threat detection and auditability.",
                "implementation_effort": "Low",
                "estimated_security_impact": "+30%",
                "aws_services": ["CloudTrail", "S3", "KMS"],
                "implementation_steps": [
                    "Create a new CloudTrail trail.",
                    "Apply it to all regions.",
                    "Send logs to a centralized S3 bucket."
                ]
            })
            
        # 3. Cost Optimization Recommendations
        cost_findings = review_findings.get("cost_findings", [])
        if any("idle" in f.lower() for f in cost_findings):
            recommendations.append({
                "id": "REC-004",
                "category": "Cost Optimization",
                "priority": "MEDIUM",
                "title": "Terminate or Rightsize Idle EC2 Instances",
                "current_state": "EC2 instances running with low utilization.",
                "recommended_state": "Resources sized to workload demands or terminated.",
                "reason": "Paying for unused compute wastes budget.",
                "business_impact": "Reduces monthly AWS bill without impacting performance.",
                "implementation_effort": "Medium",
                "estimated_cost_impact": "Varies",
                "aws_services": ["EC2", "Compute Optimizer", "Cost Explorer"],
                "implementation_steps": [
                    "Review Compute Optimizer recommendations.",
                    "Snapshot idle instances.",
                    "Terminate or downgrade instance sizes."
                ]
            })

        # 4. Monitoring Recommendations
        if inventory.get("cloudwatch_alarms", 0) == 0:
            recommendations.append({
                "id": "REC-005",
                "category": "Monitoring",
                "priority": "MEDIUM",
                "title": "Configure CloudWatch Alarms",
                "current_state": "No automated alerts for high CPU or memory.",
                "recommended_state": "CloudWatch Alarms triggering SNS notifications.",
                "reason": "Without alerts, failures and performance degradation go unnoticed.",
                "business_impact": "Reduces Mean Time to Detect (MTTD).",
                "implementation_effort": "Low",
                "aws_services": ["CloudWatch", "SNS"],
                "implementation_steps": [
                    "Create SNS Topic for alerts.",
                    "Create CloudWatch Alarms for CPU > 80%.",
                    "Route alarms to SNS."
                ]
            })

        # Default recommendation if none matched
        if not recommendations:
            recommendations.append({
                "id": "REC-000",
                "category": "Operational Excellence",
                "priority": "LOW",
                "title": "Review AWS Well-Architected Framework",
                "current_state": "Architecture meets baseline checks.",
                "recommended_state": "Continuous improvement using AWS best practices.",
                "reason": "Continuous evolution is key to cloud maturity.",
                "business_impact": "Maintains a high standard of operations.",
                "implementation_effort": "Low",
                "aws_services": ["Well-Architected Tool"],
                "implementation_steps": ["Schedule quarterly architecture reviews."]
            })

        # Sort recommendations by priority
        priority_map = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        recommendations.sort(key=lambda x: priority_map.get(x["priority"], 99))
        
        return recommendations
