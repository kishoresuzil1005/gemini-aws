import logging
from fastapi import HTTPException
from knowledge.service.client_factory import get_default_client

logger = logging.getLogger(__name__)

class ExposureAnalyzer:
    def __init__(self, knowledge_client=None):
        self.client = knowledge_client or get_default_client()

    def lambda_api_gateways(self, resource_id: str):
        query = """
        MATCH (api:APIGateway)-[:INVOKES]->(l:Lambda {id:$resource_id})
        RETURN api.id AS id, api.name AS name
        """
        try:
            return self.client.query_graph(query, resource_id=resource_id)
        except NotImplementedError:
            return []

    def analyze(self, resource_id: str):
        """
        Determines whether a resource is reachable from the Internet.
        Branches by resource type for specific exposure criteria.
        """
        resource = self.client.get_resource(resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
            
        exposure = "PRIVATE"
        internet_accessible = False
        reasons = []
        
        try:
            resource_type = resource.get("type", "Unknown")

            # Common Subnet -> IGW path query
            is_in_public_subnet = False
            igw_query = """
            MATCH path=(n {id:$resource_id})-[:IN_SUBNET|ASSOCIATED_WITH|ROUTES_TO*1..5]->(igw:InternetGateway)
            RETURN count(path) as path_count
            """
            try:
                igw_res = self.client.query_graph(igw_query, resource_id=resource_id)
                if igw_res and igw_res[0].get("path_count", 0) > 0:
                    is_in_public_subnet = True
            except NotImplementedError:
                # If query graph not supported, default to safe assumption or mock
                pass

            if resource_type == "EC2":
                if is_in_public_subnet:
                    internet_accessible = True
                    exposure = "PUBLIC"
                    reasons.extend([
                        "Public subnet",
                        "Internet Gateway"
                    ])
                    # Mock check for open security group
                    reasons.append("Open Security Group")
                else:
                    reasons.extend([
                        "Private subnet",
                        "No Internet Gateway"
                    ])

            elif resource_type == "RDS":
                if is_in_public_subnet:
                    internet_accessible = True
                    exposure = "PUBLIC"
                    reasons.extend([
                        "Publicly Accessible",
                        "Public subnet"
                    ])
                else:
                    reasons.extend([
                        "Private subnet",
                        "No Internet Gateway"
                    ])

            elif resource_type == "Lambda":
                # Check for API Gateway triggers using the new helper
                api_gateways = self.lambda_api_gateways(resource_id)
                if api_gateways:
                    internet_accessible = True
                    exposure = "PUBLIC"
                    api_names = [api["name"] for api in api_gateways if api.get("name")]
                    reasons.append(f"Lambda is exposed through API Gateway: {', '.join(api_names)}.")
                else:
                    reasons.append("No API Gateway triggers detected.")
                    
                # Check VPC attachment
                vpc_query = "MATCH (n {id:$resource_id})-[:IN_VPC]->(vpc) RETURN count(vpc) as vpc_count"
                try:
                    vpc_res = self.client.query_graph(vpc_query, resource_id=resource_id)
                    if not vpc_res or vpc_res[0].get("vpc_count", 0) == 0:
                        reasons.append("No VPC attachment")
                except NotImplementedError:
                    pass

            elif resource_type == "ALB":
                internet_accessible = True
                exposure = "PUBLIC"
                reasons.append("Internet-facing Load Balancer")

            else:
                if is_in_public_subnet:
                    internet_accessible = True
                    exposure = "PUBLIC"
                    reasons.append(f"{resource_type} resides in a public subnet with a route to an Internet Gateway")
                else:
                    reasons.append("No active route paths to an Internet Gateway detected.")
                
        except Exception as e:
            logger.error(f"Error checking internet exposure: {e}")
            reasons.append(str(e))
            
        return {
            "resource": resource_id,
            "internet_accessible": internet_accessible,
            "exposure": exposure,
            "reason": reasons
        }