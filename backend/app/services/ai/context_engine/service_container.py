"""Service Container and dependencies for the Context Engine.

This module provides the central Dependency Injection container and the
service wrappers that encapsulate external clients (e.g., boto3).
Providers rely entirely on these services rather than instantiating
clients or database sessions themselves.
"""

import boto3
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Service Wrappers
# -----------------------------------------------------------------------------

class CloudWatchService:
    """Encapsulates AWS CloudWatch API calls."""
    
    def get_metric_data(self, metric_queries: List[Dict], start_time: Any, end_time: Any) -> Dict[str, Any]:
        client = boto3.client("cloudwatch")
        return client.get_metric_data(
            MetricDataQueries=metric_queries,
            StartTime=start_time,
            EndTime=end_time,
        )


class IAMService:
    """Encapsulates AWS IAM API calls."""

    def get_role(self, role_name: str) -> Dict[str, Any]:
        client = boto3.client("iam")
        return client.get_role(RoleName=role_name)

    def list_attached_role_policies(self, role_name: str) -> List[Dict[str, Any]]:
        client = boto3.client("iam")
        paginator = client.get_paginator("list_attached_role_policies")
        policies = []
        for page in paginator.paginate(RoleName=role_name):
            policies.extend(page.get("AttachedPolicies", []))
        return policies

    def list_roles(self) -> List[Dict[str, Any]]:
        client = boto3.client("iam")
        paginator = client.get_paginator("list_roles")
        roles = []
        for page in paginator.paginate():
            roles.extend(page.get("Roles", []))
        return roles
        
    def resolve_instance_profile_role(self, resource_id: str) -> str:
        """Find the IAM role associated with an EC2 instance."""
        try:
            ec2 = boto3.client("ec2")
            resp = ec2.describe_instances(InstanceIds=[resource_id])
            reservations = resp.get("Reservations", [])
            if reservations:
                instance = reservations[0]["Instances"][0]
                profile = instance.get("IamInstanceProfile", {})
                arn = profile.get("Arn", "")
                if arn:
                    profile_name = arn.split("/")[-1]
                    iam = boto3.client("iam")
                    p_resp = iam.get_instance_profile(InstanceProfileName=profile_name)
                    roles = p_resp.get("InstanceProfile", {}).get("Roles", [])
                    if roles:
                        return roles[0].get("RoleName", "")
        except Exception as exc:
            logger.debug("IAMService resolve_instance_profile_role(%s): %s", resource_id, exc)
        return ""


class CostService:
    """Encapsulates AWS Cost Explorer operations via the existing adapter."""
    
    def _get_adapter(self):
        from app.database import SessionLocal
        from app.models import CloudAccountDB
        from app.providers.aws.cost_explorer import CostExplorerAdapter
        
        db = SessionLocal()
        try:
            acct = db.query(CloudAccountDB).filter(CloudAccountDB.provider == "AWS").first()
            account_id = acct.id if acct else 1
        finally:
            db.close()
            
        return CostExplorerAdapter(account_id)
        
    def get_current_month_cost(self) -> float:
        return self._get_adapter().get_current_month_cost()
        
    def get_daily_cost_trend(self, days: int) -> List[Dict[str, Any]]:
        return self._get_adapter().get_daily_cost_trend(days=days)


class DocumentationService:
    """Encapsulates Qdrant and internal documentation lookups."""
    
    def search_qdrant(self, resource_id: str) -> List[Dict]:
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.http.models import Filter, FieldCondition, MatchValue

            client = QdrantClient(host="localhost", port=6333, timeout=3)
            collections = [c.name for c in client.get_collections().collections]
            if not collections:
                return []

            coll = collections[0]
            results = client.scroll(
                collection_name=coll,
                scroll_filter=Filter(
                    must=[FieldCondition(key="resource_type", match=MatchValue(value=resource_id[:3].upper()))]
                ) if len(resource_id) >= 3 else None,
                limit=3,
                with_payload=True,
            )
            docs = []
            for point in results[0]:
                payload = point.payload or {}
                docs.append({
                    "type":    "qdrant",
                    "title":   payload.get("title", "Documentation"),
                    "url":     payload.get("url", ""),
                    "snippet": payload.get("content", "")[:400],
                    "score":   0.8,
                })
            return docs
        except Exception as exc:
            logger.debug("DocumentationService Qdrant search failed: %s", exc)
            return []


# -----------------------------------------------------------------------------
# Service Container
# -----------------------------------------------------------------------------

class ServiceContainer:
    """
    Central dependency container for the Context Engine.
    Creates and holds one instance of every shared service.
    """

    def __init__(self):
        from app.database import SessionLocal
        from app.services.graph.neo4j_service import Neo4jService
        
        # Core services
        self.db_session_factory = SessionLocal
        self.neo4j_service = Neo4jService()
        
        # AWS & Domain services
        self.cloudwatch_service = CloudWatchService()
        self.iam_service = IAMService()
        self.cost_service = CostService()
        self.documentation_service = DocumentationService()

    @classmethod
    def create(cls) -> "ServiceContainer":
        return cls()
