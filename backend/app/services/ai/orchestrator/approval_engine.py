from app.services.ai.orchestrator.orchestration_models import ApprovalRequirement

class ApprovalEngine:
    def determine_approval(self, resource_type: str, priority: str) -> ApprovalRequirement:
        required = priority in ["CRITICAL", "HIGH"]
        approver = None
        reason = "Safe automated remediation"
        
        if required:
            if resource_type == "IAM":
                approver = "Security Team"
                reason = "IAM Policy Modification"
            elif resource_type == "RDS":
                approver = "DBA Team"
                reason = "Database Configuration Modification"
            elif resource_type == "EC2":
                approver = "DevOps Team"
                reason = "Compute Instance Modification"
            elif resource_type == "ALB":
                approver = "Architecture Team"
                reason = "Load Balancer / Traffic Routing Modification"
            elif resource_type == "Lambda":
                approver = "DevOps Team"
                reason = "Serverless Function Modification"
            elif resource_type == "VPC":
                approver = "Cloud Team"
                reason = "VPC Configuration Modification"
            else:
                approver = "Cloud Team"
                reason = "General Infrastructure Modification"
            
        return ApprovalRequirement(
            required=required,
            approver_group=approver,
            reason=reason
        )