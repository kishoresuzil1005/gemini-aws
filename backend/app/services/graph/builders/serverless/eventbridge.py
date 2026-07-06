from typing import List, Dict
from app.models import ResourceDB


class EventBridgeGraphBuilder:

    @staticmethod
    def build(resources: List[ResourceDB]) -> List[Dict]:

        relationships = []

        lambda_lookup = {}

        for resource in resources:
            if resource.resource_type == "Lambda":
                lambda_lookup[resource.resource_id] = resource

        for rule in resources:

            if rule.resource_type != "EventBridgeRule":
                continue

            metadata = rule.resource_metadata or {}

            targets = metadata.get("targets", [])

            for target in targets:

                arn = target.get("arn")

                if not arn:
                    continue

                lambda_name = arn.split(":")[-1]

                if lambda_name not in lambda_lookup:
                    continue

                relationships.append(
                    {
                        "from": rule.resource_id,
                        "to": lambda_name,
                        "type": "TRIGGERS",
                        "source_type": "EventBridgeRule",
                        "target_type": "Lambda",
                    }
                )

        return relationships
