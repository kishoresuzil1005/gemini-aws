import boto3
import logging
logger = logging.getLogger(__name__)

class EventBridgeDiscovery:

    @staticmethod
    def discover(region: str) -> list[dict]:
        resources = []
        try:
            client = boto3.client('events', region_name=region)
            next_token = None
            while True:
                kwargs = {}
                if next_token:
                    kwargs['NextToken'] = next_token
                response = client.list_event_buses(**kwargs)
                for bus in response.get('EventBuses', []):
                    bus_arn = bus['Arn']
                    bus_name = bus['Name']
                    resources.append({'resource_id': bus_arn, 'resource_type': 'EventBridgeBus', 'region': region, 'name': bus_name, 'provider': 'AWS', 'metadata': {'arn': bus_arn, 'policy': bus.get('Policy', '')}, 'dependencies': []})
                    rule_next_token = None
                    while True:
                        rule_kwargs = {'EventBusName': bus_name}
                        if rule_next_token:
                            rule_kwargs['NextToken'] = rule_next_token
                        rule_resp = client.list_rules(**rule_kwargs)
                        for rule in rule_resp.get('Rules', []):
                            rule_arn = rule['Arn']
                            rule_name = rule['Name']
                            targets = []
                            try:
                                targets_resp = client.list_targets_by_rule(Rule=rule_name, EventBusName=bus_name)
                                targets = [{'id': t.get('Id'), 'arn': t.get('Arn')} for t in targets_resp.get('Targets', [])]
                            except Exception:
                                pass
                            resources.append({'resource_id': rule_arn, 'resource_type': 'EventBridgeRule', 'region': region, 'name': rule_name, 'status': rule.get('State'), 'provider': 'AWS', 'metadata': {'arn': rule_arn, 'bus_name': bus_name, 'bus_arn': bus_arn, 'description': rule.get('Description', ''), 'schedule_expression': rule.get('ScheduleExpression', ''), 'event_pattern': rule.get('EventPattern', ''), 'targets': targets, 'target_arns': [t['arn'] for t in targets]}, 'dependencies': []})
                        rule_next_token = rule_resp.get('NextToken')
                        if not rule_next_token:
                            break
                next_token = response.get('NextToken')
                if not next_token:
                    break
        except Exception:
            logger.exception('EventBridge discovery failed for region %s', region)
        return resources