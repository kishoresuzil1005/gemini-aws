"""DocumentationProvider – retrieves documentation in priority order.

Source priority
---------------
1. **Internal** – ``ResourceSnapshotDB`` configuration hints + metadata.
2. **Qdrant** – semantic vector search against ingested documentation.
3. **AWS** – static documentation URI derived from resource type.

Each source is tried in order; the first that returns results wins.
All three sources are always queried in Phase 2 so the full list of
matches is available to the AI.
"""

import time
import logging
from typing import Any, Dict, List

from ..base_provider import BaseProvider
from ..common.constants import DOCUMENTATION_PROVIDER_ENABLED, TTL_STATIC
from ..common.helpers import flag_enabled
from ..enums import ContextLevel, ProviderScope
from ..request import ContextRequest
from ..resolved_resource import ResolvedResource

logger = logging.getLogger(__name__)

# AWS documentation URL patterns by resource type prefix
AWS_DOCS_MAP: Dict[str, str] = {
    "EC2":          "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/",
    "RDS":          "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/",
    "S3":           "https://docs.aws.amazon.com/AmazonS3/latest/userguide/",
    "Lambda":       "https://docs.aws.amazon.com/lambda/latest/dg/",
    "EKS":          "https://docs.aws.amazon.com/eks/latest/userguide/",
    "ECS":          "https://docs.aws.amazon.com/AmazonECS/latest/developerguide/",
    "IAM":          "https://docs.aws.amazon.com/IAM/latest/UserGuide/",
    "DynamoDB":     "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/",
    "ElastiCache":  "https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/",
    "ELB":          "https://docs.aws.amazon.com/elasticloadbalancing/latest/application/",
    "CloudFront":   "https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/",
    "SNS":          "https://docs.aws.amazon.com/sns/latest/dg/",
    "SQS":          "https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/",
    "VPC":          "https://docs.aws.amazon.com/vpc/latest/userguide/",
    "Route53":      "https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/",
}


class DocumentationProvider(BaseProvider):
    """Retrieves documentation from internal, Qdrant, and AWS sources."""

    name       = "documentation"
    scope      = ProviderScope.STATIC
    priority   = 40
    output_key = "documentation"
    cache_ttl  = TTL_STATIC
    version    = "1.0"
    source     = "multi"
    enabled    = flag_enabled(DOCUMENTATION_PROVIDER_ENABLED)

    def __init__(self, *, db_session_factory, documentation_service):
        super().__init__()
        self.db_session_factory = db_session_factory
        self.documentation_service = documentation_service

    def supports(self, level: ContextLevel) -> bool:
        return level in (ContextLevel.FULL, ContextLevel.DEEP)

    async def fetch(self, resource: ResolvedResource, request: ContextRequest) -> Dict[str, Any]:
        t0 = time.monotonic()
        sources: List[Dict] = []

        # 1. Internal docs (always try first)
        internal = self._search_internal(resource.resource_id)
        sources.extend(internal)

        # 2. Qdrant semantic search
        qdrant = self.documentation_service.search_qdrant(resource.resource_id)
        sources.extend(qdrant)

        # 3. AWS official documentation
        aws = self._search_aws_docs(resource.resource_id)
        sources.extend(aws)

        primary_source = sources[0]["type"] if sources else None

        data: Dict[str, Any] = {
            "sources":        sources,
            "primary_source": primary_source,
        }

        exec_ms = (time.monotonic() - t0) * 1000
        return self._build_response(data, execution_time_ms=exec_ms)

    # ------------------------------------------------------------------
    #  Source: Internal (ResourceSnapshotDB + configuration_hint)
    # ------------------------------------------------------------------

    def _search_internal(self, resource_id: str) -> List[Dict]:
        try:
            from app.models import ResourceDB, ResourceSnapshotDB

            db = self.db_session_factory()
            try:
                row = db.query(ResourceDB).filter(
                    ResourceDB.resource_id == resource_id
                ).first()

                docs = []
                if row and row.configuration_hint:
                    docs.append({
                        "type":    "internal",
                        "title":   f"Configuration Guide – {row.resource_type}",
                        "url":     "",
                        "snippet": row.configuration_hint[:500],
                        "score":   1.0,
                    })

                snap = db.query(ResourceSnapshotDB).filter(
                    ResourceSnapshotDB.resource_id == resource_id
                ).order_by(ResourceSnapshotDB.created_at.desc()).first()

                if snap:
                    import json
                    try:
                        snap_data = json.loads(snap.snapshot_json)
                        docs.append({
                            "type":    "internal",
                            "title":   f"Resource Snapshot – {resource_id}",
                            "url":     "",
                            "snippet": str(snap_data)[:500],
                            "score":   0.9,
                        })
                    except Exception:
                        pass

                return docs
            finally:
                db.close()

        except Exception as exc:
            logger.debug("DocumentationProvider internal search failed: %s", exc)
            return []

    # ------------------------------------------------------------------
    #  Source: AWS Official Documentation
    # ------------------------------------------------------------------

    def _search_aws_docs(self, resource_id: str) -> List[Dict]:
        """
        Map the resource type to the corresponding AWS documentation URL.
        """
        try:
            from app.models import ResourceDB

            db = self.db_session_factory()
            try:
                row = db.query(ResourceDB).filter(
                    ResourceDB.resource_id == resource_id
                ).first()
                resource_type = row.resource_type if row else ""
            finally:
                db.close()
        except Exception:
            resource_type = ""

        # Try to match resource type to documentation URL
        url = ""
        for key, doc_url in AWS_DOCS_MAP.items():
            if key.lower() in resource_type.lower():
                url = doc_url
                break

        if not url:
            return []

        return [{
            "type":    "aws",
            "title":   f"AWS {resource_type} Documentation",
            "url":     url,
            "snippet": f"Official AWS documentation for {resource_type}.",
            "score":   0.7,
        }]
