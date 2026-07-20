"""IAMProvider – fetches normalized IAM data from AWS and maps to a cloud-agnostic schema.

Uses boto3 to call AWS IAM APIs (roles, policies, trust relationships,
permission boundaries) and maps the result to a provider-agnostic schema
so that Azure / GCP implementations can produce the same structure later.

Phase 2 scope: roles, attached policies, trust relationships, permission
boundaries.  Inline policy documents are deferred to IAMAnalyzer.
"""

import time
import logging
from typing import Any, Dict, List

import boto3

from ..base_provider import BaseProvider
from ..common.constants import IAM_PROVIDER_ENABLED, TTL_STATIC
from ..common.helpers import flag_enabled
from ..enums import ContextLevel, ProviderScope
from ..request import ContextRequest
from ..resolved_resource import ResolvedResource

logger = logging.getLogger(__name__)


class IAMProvider(BaseProvider):
    """Fetches normalized IAM data for a resource."""

    name       = "iam"
    scope      = ProviderScope.STATIC
    priority   = 30
    output_key = "security"
    cache_ttl  = TTL_STATIC
    version    = "1.0"
    source     = "aws_iam"
    enabled    = flag_enabled(IAM_PROVIDER_ENABLED)

    def __init__(self, *, iam_service):
        super().__init__()
        self.iam_service = iam_service

    def supports(self, level: ContextLevel) -> bool:
        return level in (ContextLevel.FULL, ContextLevel.DEEP)

    async def fetch(self, resource: ResolvedResource, request: ContextRequest) -> Dict[str, Any]:
        t0 = time.monotonic()
        data = self._fetch_iam(resource.resource_id)
        exec_ms = (time.monotonic() - t0) * 1000
        return self._build_response(data, execution_time_ms=exec_ms)

    # ------------------------------------------------------------------

    def _fetch_iam(self, resource_id: str) -> Dict[str, Any]:
        identities: List[Dict] = []
        permissions: List[Dict] = []
        trust_relationships: List[Dict] = []
        permission_boundaries: List[Dict] = []

        try:
            svc = self.iam_service

            # Attempt to resolve the resource as an EC2 instance profile role
            role_name = svc.resolve_instance_profile_role(resource_id)

            if role_name:
                try:
                    role_resp = svc.get_role(role_name)
                    role = role_resp.get("Role", {})

                    # Identity
                    identities.append({
                        "id":   role.get("RoleId", ""),
                        "name": role.get("RoleName", role_name),
                        "type": "role",
                        "arn":  role.get("Arn", ""),
                    })

                    # Trust relationships
                    trust_doc = role.get("AssumeRolePolicyDocument", {})
                    for stmt in trust_doc.get("Statement", []):
                        principal = stmt.get("Principal", {})
                        p_type = "Service" if "Service" in principal else (
                            "Federated" if "Federated" in principal else "Account"
                        )
                        p_value = (
                            principal.get("Service") or
                            principal.get("Federated") or
                            principal.get("AWS") or
                            ""
                        )
                        trust_relationships.append({
                            "principal":  p_value if isinstance(p_value, str) else str(p_value),
                            "type":       p_type,
                            "conditions": stmt.get("Condition", {}),
                        })

                    # Permission boundary
                    pb = role.get("PermissionsBoundary", {})
                    if pb:
                        permission_boundaries.append({
                            "policy_arn":  pb.get("PermissionsBoundaryArn", ""),
                            "description": "Permission boundary",
                        })

                    # Attached managed policies
                    attached = svc.list_attached_role_policies(role_name)
                    for pol in attached:
                        permissions.append({
                            "principal": role.get("Arn", role_name),
                            "actions":   ["*"],
                            "resources": ["*"],
                            "effect":    "Allow",
                            "policy_name": pol.get("PolicyName", ""),
                            "policy_arn":  pol.get("PolicyArn", ""),
                        })

                except Exception as exc:
                    logger.debug("IAMProvider role fetch for %s: %s", role_name, exc)

            else:
                # Fallback: list roles that match resource prefix/name
                try:
                    all_roles = svc.list_roles()
                    for r in all_roles:
                        if resource_id in r.get("RoleName", "") or resource_id in r.get("Arn", ""):
                            identities.append({
                                "id":   r.get("RoleId", ""),
                                "name": r.get("RoleName", ""),
                                "type": "role",
                                "arn":  r.get("Arn", ""),
                            })
                except Exception:
                    pass

        except Exception as exc:
            logger.warning("IAMProvider failed for %s: %s", resource_id, exc)

        return {
            "identities":            identities,
            "permissions":           permissions,
            "trust_relationships":   trust_relationships,
            "permission_boundaries": permission_boundaries,
        }
