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

    def supports(self, level: ContextLevel) -> bool:
        return level in (ContextLevel.FULL, ContextLevel.DEEP)

    async def fetch(self, resource: ResolvedResource, request: ContextRequest) -> Dict[str, Any]:
        t0 = time.monotonic()
        data = self._fetch_iam(resource.resource_id)
        exec_ms = (time.monotonic() - t0) * 1000
        return self._build_response(data, execution_time_ms=exec_ms)

    # ------------------------------------------------------------------

    def _fetch_iam(self, resource_id: str) -> Dict[str, Any]:
        """
        Determine the IAM principal associated with the resource and fetch
        its roles, policies, trust relationships, and permission boundaries.

        For Phase 2 we collect:
         - IAM roles attached to the instance profile (EC2 instances)
         - Inline + attached managed policies
         - Trust relationship principals
         - Permission boundaries on the role
        """
        identities: List[Dict] = []
        permissions: List[Dict] = []
        trust_relationships: List[Dict] = []
        permission_boundaries: List[Dict] = []

        try:
            client = boto3.client("iam")

            # Attempt to resolve the resource as an EC2 instance profile role
            role_name = self._resolve_role_for_resource(resource_id)

            if role_name:
                try:
                    role_resp = client.get_role(RoleName=role_name)
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
                    pag = client.get_paginator("list_attached_role_policies")
                    for page in pag.paginate(RoleName=role_name):
                        for pol in page.get("AttachedPolicies", []):
                            permissions.append({
                                "principal": role.get("Arn", role_name),
                                "actions":   ["*"],   # full expansion deferred to IAMAnalyzer
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
                    role_pag = client.get_paginator("list_roles")
                    for page in role_pag.paginate():
                        for r in page.get("Roles", []):
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

    def _resolve_role_for_resource(self, resource_id: str) -> str:
        """
        Try to find the IAM role associated with an EC2 instance
        by looking at its instance profile.
        """
        if not resource_id.startswith("i-"):
            return ""
        try:
            ec2 = boto3.client("ec2")
            resp = ec2.describe_instances(InstanceIds=[resource_id])
            reservations = resp.get("Reservations", [])
            if reservations:
                instance = reservations[0]["Instances"][0]
                profile = instance.get("IamInstanceProfile", {})
                arn = profile.get("Arn", "")
                if arn:
                    # ARN format: arn:aws:iam::ACCOUNT:instance-profile/PROFILE_NAME
                    profile_name = arn.split("/")[-1]
                    iam = boto3.client("iam")
                    p_resp = iam.get_instance_profile(InstanceProfileName=profile_name)
                    roles = p_resp.get("InstanceProfile", {}).get("Roles", [])
                    if roles:
                        return roles[0].get("RoleName", "")
        except Exception as exc:
            logger.debug("_resolve_role_for_resource(%s): %s", resource_id, exc)
        return ""
