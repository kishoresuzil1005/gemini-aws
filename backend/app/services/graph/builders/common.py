from typing import List, Dict, Any
from app.models import ResourceDB

RELATIONSHIP_MAP = {
    "VPC": "IN_VPC",
    "SUBNET": "IN_SUBNET",
    "Subnet": "IN_SUBNET",
    "SECURITYGROUP": "USES_SG",
    "SecurityGroup": "USES_SG",
    "EBS": "ATTACHED_TO",
    "IAM": "USES_ROLE",
    "IAM_ROLE": "USES_ROLE",
    "IAMRole": "USES_ROLE",
    "TARGETGROUP": "TARGETS",
    "TargetGroup": "TARGETS",
    "ALB": "ATTACHED_TO",
    "LAMBDA": "INVOKES",
    "Lambda": "INVOKES",
    "S3": "USES_BUCKET",
    "S3Bucket": "USES_BUCKET",
    "RDS": "CONNECTS_TO",
    "DynamoDBTable": "CONNECTS_TO",
    "ElastiCacheRedis": "USES_CACHE",
    "ElastiCacheMemcached": "USES_CACHE",
    "ElastiCacheCluster": "USES_CACHE",
    "OpenSearchDomain": "USES_SEARCH",
    "SNSTopic": "SUBSCRIBED_TO",
    "SQSQueue": "CONNECTS_TO",
    "EventBridgeBus": "TRIGGERS",
    "EventBridgeRule": "TRIGGERS",
    "APIGateway": "INVOKES",
    "APIGatewayStage": "HOSTED_ON",
    "CloudFrontDistribution": "ROUTES_TO",
    "WAFWebACL": "PROTECTED_BY",
    "KMSKey": "ENCRYPTED_BY",
    "CloudWatchAlarm": "MONITORS",
    "CloudWatchLogGroup": "LOGS_TO",
    "ACMCertificate": "SECURED_BY",
    "RouteTable": "HAS_ROUTE",
    "InternetGateway": "ROUTES_TO",
    "NatGateway": "ROUTES_TO",
    "ElasticIP": "ATTACHED_TO",
    "NetworkInterface": "ATTACHED_TO",
    "AutoScalingGroup": "MANAGES",
    "EC2": "HOSTS",
    "ECSCluster": "HOSTS",
    "EKSCluster": "HOSTS",
    "StepFunction": "TRIGGERS",
    "SecretsManagerSecret": "USES_SECRET"
}

class GraphBuilderHelper:
    @staticmethod
    def build_edges(source: ResourceDB, resource_lookup: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Safely builds edges from a ResourceDB instance based on Phase 1 dependencies.
        Ensures target resources exist in the database (via resource_lookup).
        """
        edges = []
        metadata = source.resource_metadata or {}
        dependencies = metadata.get("dependencies", [])
        
        for dep in dependencies:
            target_id = dep.get("id")
            target_type = dep.get("type")
            
            if not target_id or not target_type:
                continue
                
            # Rule 4: Never create relationships if the target resource does not exist.
            # Special case for some broad arns that might mismatch exactly, but we try exact match.
            actual_target_type = resource_lookup.get(target_id)
            if not actual_target_type:
                continue
                
            rel_type = RELATIONSHIP_MAP.get(target_type, "CONNECTS_TO")
            
            edges.append({
                "from": source.resource_id,
                "to": target_id,
                "type": rel_type,
                "source_type": source.resource_type,
                "target_type": actual_target_type,
                "metadata": {}
            })
            
        return edges
