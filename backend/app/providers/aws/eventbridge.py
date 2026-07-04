import boto3
import logging

logger = logging.getLogger(__name__)


class EventBridgeDiscovery:

    @staticmethod
    def discover(region: str) -> list[dict]:
        resources = []
        try:
            client = boto3.client("events", region_name=region)

            # Event Buses
            paginator = client.get_paginator("list_event_buses")
            for page in paginator.paginate():
                for bus in page.get("EventBuses", []):
                    bus_arn = bus["Arn"]
                    bus_name = bus["Name"]

                    resources.append({
                        "resource_id": bus_arn,
                        "resource_type": "EventBridgeBus",
                        "region": region,
                        "name": bus_name,
                        "arn": bus_arn,
                        "policy": bus.get("Policy", ""),
                    })

                    # Rules on this bus
                    rule_paginator = client.get_paginator("list_rules")
                    for rule_page in rule_paginator.paginate(EventBusName=bus_name):
                        for rule in rule_page.get("Rules", []):
                            rule_arn = rule["Arn"]
                            rule_name = rule["Name"]

                            # Targets
                            targets = []
                            try:
                                targets_resp = client.list_targets_by_rule(
                                    Rule=rule_name,
                                    EventBusName=bus_name
                                )
                                targets = [
                                    {
                                        "id": t.get("Id"),
                                        "arn": t.get("Arn"),
                                    }
                                    for t in targets_resp.get("Targets", [])
                                ]
                            except Exception:
                                pass

                            resources.append({
                                "resource_id": rule_arn,
                                "resource_type": "EventBridgeRule",
                                "region": region,
                                "name": rule_name,
                                "arn": rule_arn,
                                "bus_name": bus_name,
                                "bus_arn": bus_arn,
                                "state": rule.get("State"),
                                "description": rule.get("Description", ""),
                                "schedule_expression": rule.get("ScheduleExpression", ""),
                                "event_pattern": rule.get("EventPattern", ""),
                                "targets": targets,
                                "target_arns": [t["arn"] for t in targets],
                            })

        except Exception:
            logger.exception("EventBridge discovery failed for region %s", region)

        return resources
