from typing import List

class PermissionEngine:
    """
    Evaluates whether a specific agent is allowed to execute a specific action 
    on a target resource.
    """
    def __init__(self):
        self.role_bindings = {
            "security_agent": ["iam:*", "kms:*", "vpc:Analyze"],
            "networking_agent": ["vpc:*", "ec2:DescribeNetwork*"],
            "infrastructure_agent": ["ec2:*", "eks:*"],
            "database_agent": ["rds:*", "dynamodb:*"],
            "finops_agent": ["ce:*", "budgets:*"],
            "sre_agent": ["cloudwatch:*", "sns:*"],
            "kubernetes_agent": ["eks:*", "k8s:*"]
        }

    def check_permission(self, agent_domain: str, action: str) -> bool:
        """
        Mock RBAC evaluation. In reality, integrates with IAM/OPA policies.
        """
        agent_role = f"{agent_domain}_agent"
        allowed_actions = self.role_bindings.get(agent_role, [])
        
        # Simple glob matching
        for allowed in allowed_actions:
            if allowed == "*:*" or allowed == "*":
                return True
            prefix = allowed.split(":")[0]
            if allowed.endswith("*") and action.startswith(prefix):
                return True
            if action == allowed:
                return True
                
        return False
