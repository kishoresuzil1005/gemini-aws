class RecommendationEngine:
    def __init__(self):
        pass

    def generate(self, findings: list):
        """
        Takes raw findings from other analyzers and generates actionable 
        remediation steps.
        """
        recommendations = set()
        
        for finding in findings:
            f_type = finding.get("type", "")
            
            if f_type in ["PUBLIC_ACCESS", "NETWORK_PUBLIC", "PUBLIC_SUBNET"]:
                recommendations.add("Consider moving this workload to a Private Subnet and exposing via ALB/NAT.")
            elif f_type in ["OPEN_SSH", "MOCK_PORT_ANALYSIS", "SSH_OPEN"]:
                recommendations.add("Restrict SSH (Port 22) access to a VPN or specific bastion host IPs rather than 0.0.0.0/0.")
            elif f_type in ["MOCK_IAM_ANALYSIS", "HIGH_PRIVILEGE", "IAM_OVER_PRIVILEGED"]:
                recommendations.add("Implement Least Privilege Policy. Avoid using AdministratorAccess for compute roles.")
            elif f_type == "WAF_MISSING":
                recommendations.add("Attach a Web Application Firewall (WAF) to this Load Balancer to protect against common web exploits.")
            elif f_type == "VPC_ATTACHMENT_MISSING":
                recommendations.add("Attach Lambda to a VPC if it requires access to private resources like RDS or ElastiCache.")
                
        # Default recommendation if high risk but no specific mapping
        if not recommendations and any(f.get("severity") in ["HIGH", "CRITICAL"] for f in findings):
            recommendations.add("Review AWS well-architected framework for this resource type.")
            
        return list(recommendations)
