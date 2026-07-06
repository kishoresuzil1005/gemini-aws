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
            
            if f_type == "PUBLIC_ACCESS" or f_type == "NETWORK_PUBLIC":
                recommendations.add("Consider moving this workload to a Private Subnet and exposing via ALB/NAT.")
            elif f_type == "OPEN_SSH" or f_type == "MOCK_PORT_ANALYSIS":
                recommendations.add("Restrict SSH (Port 22) access to a VPN or specific bastion host IPs rather than 0.0.0.0/0.")
            elif f_type == "MOCK_IAM_ANALYSIS" or f_type == "HIGH_PRIVILEGE":
                recommendations.add("Implement Least Privilege Policy. Avoid using AdministratorAccess for compute roles.")
                
        # Default recommendation if high risk but no specific mapping
        if not recommendations and any(f.get("severity") in ["HIGH", "CRITICAL"] for f in findings):
            recommendations.add("Review AWS well-architected framework for this resource type.")
            
        return list(recommendations)
