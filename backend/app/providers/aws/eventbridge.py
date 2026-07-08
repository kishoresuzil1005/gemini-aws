import boto3
import logging
from app.providers.aws.models import NormalizedResource, ResourceDependency

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
                    
                    tags = {}
                    try:
                        tags_resp = client.list_tags_for_resource(ResourceARN=bus_arn)
                        tags = {t['Key']: t['Value'] for t in tags_resp.get('Tags', [])}
                    except Exception: pass
                    
                    dependencies = []
                    
                    res = NormalizedResource(
                        resource_id=bus_arn,
                        resource_type='EventBridgeBus',
                        region=region,
                        name=bus_name,
                        status='Active',
                        metadata={
                            'arn': bus_arn
                        },
                        security={
                            'policy': bus.get('Policy', '')
                        },
                        configuration={},
                        tags=tags,
                        dependencies=dependencies
                    )
                    resources.append(res.dict())
                    
                    rule_next_token = None
                    while True:
                        rule_kwargs = {'EventBusName': bus_name}
                        if rule_next_token:
                            rule_kwargs['NextToken'] = rule_next_token
                        rule_resp = client.list_rules(**rule_kwargs)
                        for rule in rule_resp.get('Rules', []):
                            rule_arn = rule['Arn']
                            rule_name = rule['Name']
                            
                            rule_tags = {}
                            try:
                                r_tags_resp = client.list_tags_for_resource(ResourceARN=rule_arn)
                                rule_tags = {t['Key']: t['Value'] for t in r_tags_resp.get('Tags', [])}
                            except Exception: pass
                            
                            rule_dependencies = [ResourceDependency(type='EventBridgeBus', id=bus_arn)]
                            
                            targets = []
                            try:
                                targets_resp = client.list_targets_by_rule(Rule=rule_name, EventBusName=bus_name)
                                for t in targets_resp.get('Targets', []):
                                    t_arn = t.get('Arn')
                                    targets.append({'id': t.get('Id'), 'arn': t_arn})
                                    if t_arn:
                                        if ':lambda:' in t_arn:
                                            rule_dependencies.append(ResourceDependency(type='Lambda', id=t_arn))
                                        elif ':sqs:' in t_arn:
                                            rule_dependencies.append(ResourceDependency(type='SQSQueue', id=t_arn))
                                        elif ':sns:' in t_arn:
                                            rule_dependencies.append(ResourceDependency(type='SNSTopic', id=t_arn))
                                        elif ':states:' in t_arn:
                                            rule_dependencies.append(ResourceDependency(type='StepFunction', id=t_arn))
                            except Exception:
                                pass
                                
                            rule_res = NormalizedResource(
                                resource_id=rule_arn,
                                resource_type='EventBridgeRule',
                                region=region,
                                name=rule_name,
                                status=rule.get('State', 'Unknown'),
                                metadata={
                                    'arn': rule_arn,
                                    'bus_name': bus_name,
                                    'bus_arn': bus_arn,
                                    'description': rule.get('Description', '')
                                },
                                configuration={
                                    'schedule_expression': rule.get('ScheduleExpression', ''),
                                    'event_pattern': rule.get('EventPattern', ''),
                                    'targets': targets,
                                    'target_arns': [t['arn'] for t in targets]
                                },
                                tags=rule_tags,
                                dependencies=rule_dependencies
                            )
                            resources.append(rule_res.dict())
                            
                        rule_next_token = rule_resp.get('NextToken')
                        if not rule_next_token:
                            break
                            
                next_token = response.get('NextToken')
                if not next_token:
                    break
        except Exception:
            logger.exception('EventBridge discovery failed for region %s', region)
        return resources