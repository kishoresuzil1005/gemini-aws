import logging
from fastapi import HTTPException
from app.services.graph.neo4j_service import Neo4jService

logger = logging.getLogger(__name__)

class ExposureAnalyzer:
    def __init__(self, neo4j_service: Neo4jService):
        self.neo4j = neo4j_service

    def analyze(self, resource_id: str):
        """
        Determines whether a resource is reachable from the Internet.
        Branches by resource type for specific exposure criteria.
        """
        if not self.neo4j.node_exists(resource_id):
            raise HTTPException(status_code=404, detail="Resource not found")
            
        exposure = "PRIVATE"
        internet_accessible = False
        reasons = []
        
        if not self.neo4j.driver:
            return {
                "resource": resource_id,
                "internet_accessible": False,
                "exposure": "UNKNOWN (Graph Disconnected)",
                "reason": ["Neo4j not connected"]
            }

        try:
            # First, find the resource type
            resource_type = "Unknown"
            type_query = "MATCH (n {id:$resource_id}) RETURN labels(n)[0] as type"
            res = self.neo4j.query(type_query, resource_id=resource_id)
            if res and res[0].get("type"):
                resource_type = res[0]["type"]

            # Common Subnet -> IGW path query
            is_in_public_subnet = False
            igw_query = """
            MATCH path=(n {id:$resource_id})-[:IN_SUBNET|ASSOCIATED_WITH|ROUTES_TO*1..5]->(igw:InternetGateway)
            RETURN count(path) as path_count
            """
            igw_res = self.neo4j.query(igw_query, resource_id=resource_id)
            if igw_res and igw_res[0]["path_count"] > 0:
                is_in_public_subnet = True

            if resource_type == "EC2":
                if is_in_public_subnet:
                    internet_accessible = True
                    exposure = "PUBLIC"
                    reasons.append("EC2 resides in a Public Subnet with a route to an Internet Gateway")
                else:
                    reasons.append("EC2 is in a Private Subnet (No route to IGW)")
                # Mock Public IP check
                reasons.append("Security Groups and Public IP need verification for full access")

            elif resource_type == "RDS":
                if is_in_public_subnet:
                    internet_accessible = True
                    exposure = "PUBLIC"
                    reasons.append("RDS is publicly accessible (in a Public Subnet)")
                else:
                    reasons.append("RDS is safely deployed in a Private Subnet")
                reasons.append("Security Group rules govern specific database port access")

            elif resource_type == "Lambda":
                # Check for API Gateway triggers
                api_query = """
                MATCH (api:ApiGateway)-[:TRIGGERS]->(n {id:$resource_id})
                RETURN count(api) as api_count
                """
                api_res = self.neo4j.query(api_query, resource_id=resource_id)
                if api_res and api_res[0]["api_count"] > 0:
                    internet_accessible = True
                    exposure = "PUBLIC"
                    reasons.append("Lambda is exposed via an API Gateway Trigger")
                else:
                    reasons.append("No API Gateway triggers detected")
                reasons.append("Public Function URL status is unverified")
                
                # Check VPC attachment
                vpc_query = "MATCH (n {id:$resource_id})-[:IN_VPC]->(vpc) RETURN count(vpc) as vpc_count"
                vpc_res = self.neo4j.query(vpc_query, resource_id=resource_id)
                if vpc_res and vpc_res[0]["vpc_count"] > 0:
                    reasons.append("Lambda is attached to a VPC")
                else:
                    reasons.append("Lambda is NOT attached to a VPC")

            elif resource_type == "ALB":
                internet_accessible = True
                exposure = "PUBLIC"
                reasons.append("ALB is assumed Internet Facing")
                reasons.append("HTTPS Listener and WAF attachment require metadata verification")

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
