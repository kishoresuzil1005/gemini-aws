"""AWS Config Service — Production"""
import logging
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)


class ConfigService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.role_arn = role_arn

    def _client(self):
        return client_factory.get_aws_client("config", region_name=self.region, role_arn=self.role_arn)

    def list(self) -> List[Dict[str, Any]]:
        return self.list_rules()

    def list_rules(self) -> List[Dict[str, Any]]:
        paginator = self._client().get_paginator("describe_config_rules")
        rules = []
        for page in paginator.paginate():
            for rule in page.get("ConfigRules", []):
                rules.append({
                    "resource_id": rule.get("ConfigRuleArn", rule.get("ConfigRuleName")),
                    "resource_type": "ConfigRule",
                    "name": rule.get("ConfigRuleName"),
                    "region": self.region,
                    "status": rule.get("ConfigRuleState", "ACTIVE"),
                    "metadata": {
                        "description": rule.get("Description"),
                        "scope": rule.get("Scope", {}),
                        "source": rule.get("Source", {}),
                        "maximum_execution_frequency": rule.get("MaximumExecutionFrequency"),
                    },
                })
        return rules

    def get_compliance_by_rule(self, rule_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        kwargs: Dict[str, Any] = {}
        if rule_names:
            kwargs["ConfigRuleNames"] = rule_names
        paginator = self._client().get_paginator("describe_compliance_by_config_rule")
        compliance = []
        for page in paginator.paginate(**kwargs):
            compliance.extend(page.get("ComplianceByConfigRules", []))
        return compliance

    def get_resource_config_history(self, resource_type: str, resource_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        resp = self._client().get_resource_config_history(
            resourceType=resource_type, resourceId=resource_id, limit=limit
        )
        return resp.get("configurationItems", [])

    def list_discovered_resources(self, resource_type: str) -> List[Dict[str, Any]]:
        paginator = self._client().get_paginator("list_discovered_resources")
        resources = []
        for page in paginator.paginate(resourceType=resource_type):
            resources.extend(page.get("resourceIdentifiers", []))
        return resources

    def get_compliance_summary(self) -> Dict[str, Any]:
        resp = self._client().get_compliance_summary_by_config_rule()
        return resp.get("ComplianceSummary", {})
