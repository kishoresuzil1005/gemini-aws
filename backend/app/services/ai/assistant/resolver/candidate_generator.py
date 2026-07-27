import logging
from typing import List, Dict, Any
from app.services.graph.neo4j_service import Neo4jService

logger = logging.getLogger(__name__)

RESOURCE_LABEL_MAP = {
    "ec2": "EC2",
    "vpc": "VPC",
    "subnet": "Subnet",
    "securitygroup": "SecurityGroup",
    "sg": "SecurityGroup",
    "lambda": "Lambda",
    "rds": "RDS",
    "database": "RDS",
    "s3": "S3",
    "bucket": "S3",
    "iam": "IAM",
    "iamrole": "IAMRole",
    "role": "IAMRole",
    "cloudfront": "CloudFront",
    "alb": "ALB",
    "targetgroup": "TargetGroup",
    "routetable": "RouteTable",
    "networkinterface": "NetworkInterface",
    "elasticip": "ElasticIP",
    "autoscalinggroup": "AutoScalingGroup",
    "dynamodbtable": "DynamoDBTable",
    "apigateway": "APIGateway",
    "eventbridgebus": "EventBridgeBus",
    "server": "EC2"
}

class CandidateGenerator:
    """Fetches candidate resources from the graph database using extracted entities."""
    
    def __init__(self):
        self.neo4j = Neo4jService()
        
    def generate(self, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Queries Neo4j for resources matching the extracted IDs or keywords."""
        candidates = []
        
        # 1. Exact ID lookup
        resource_ids = entities.get("resource_ids", [])
        if resource_ids:
            query = """
            MATCH (n:AWSResource)
            WHERE n.id IN $ids OR n.arn IN $ids
            RETURN n.id AS id, n.name AS name, labels(n) AS type
            """
            try:
                records = self.neo4j.query(query, ids=resource_ids)
                candidates.extend([dict(r) for r in records])
            except Exception as e:
                logger.error(f"Error querying Neo4j in CandidateGenerator (IDs): {e}")
            
        # 2. Keyword lookup (Fuzzy match)
        keywords = entities.get("keywords", [])
        if keywords:
            # Check if any keyword matches a known resource type
            labels = []
            for kw in keywords:
                mapped = RESOURCE_LABEL_MAP.get(kw.lower())
                if mapped and mapped not in labels:
                    labels.append(mapped)
                    
            label_match = f":{labels[0]}" if labels else ""
            
            # We match if ANY keyword matches id, name, or arn.
            query = f"""
            MATCH (n:AWSResource{label_match})
            WHERE ANY(word IN $words WHERE 
                toLower(n.id) CONTAINS word OR 
                toLower(coalesce(n.name, '')) CONTAINS word OR 
                toLower(coalesce(n.arn, '')) CONTAINS word)
            RETURN n.id AS id, n.name AS name, labels(n) AS type
            LIMIT 15
            """
            
            # Also, if a label was found but no specific resource name was given,
            # we might want to return all resources of that type if there are only a few.
            # But the keyword search above will also match the type word if it happens to be in the name/id.
            # If they just say "Why is my EC2 unhealthy", word="ec2" will match label EC2, 
            # and might not match id/name. So we should also allow match if the label is present.
            query_fallback = f"""
            MATCH (n:AWSResource{label_match})
            RETURN n.id AS id, n.name AS name, labels(n) AS type
            LIMIT 15
            """
            
            try:
                records = self.neo4j.query(query, words=keywords)
                if not records and label_match:
                    # If keyword didn't match id/name but matched a label, just return resources of that label
                    records = self.neo4j.query(query_fallback)
                    
                existing_ids = {c["id"] for c in candidates}
                for r in records:
                    if r["id"] not in existing_ids:
                        candidates.append(dict(r))
            except Exception as e:
                logger.error(f"Error querying Neo4j in CandidateGenerator (Keywords): {e}")
                
        return candidates
