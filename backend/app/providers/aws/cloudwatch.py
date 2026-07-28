import datetime
import boto3
import logging
from typing import Optional
from app.providers.aws.auth import get_aws_client
from app.providers.aws.models import NormalizedResource, ResourceDependency

logger = logging.getLogger("CloudWatchMetrics")

class CloudWatchDiscovery:
    @staticmethod
    def discover(region: str) -> list[dict]:
        resources = []
        try:
            client = boto3.client('cloudwatch', region_name=region)
            paginator = client.get_paginator('describe_alarms')
            
            for page in paginator.paginate():
                for alarm in page.get('MetricAlarms', []):
                    alarm_arn = alarm['AlarmArn']
                    alarm_name = alarm['AlarmName']
                    
                    dependencies = []
                    
                    for action in alarm.get('AlarmActions', []) + alarm.get('OKActions', []) + alarm.get('InsufficientDataActions', []):
                        if ':sns:' in action:
                            dependencies.append(ResourceDependency(type='SNSTopic', id=action))
                        elif ':autoscaling:' in action:
                            dependencies.append(ResourceDependency(type='AutoScalingGroup', id=action.split(':autoScalingGroupName/')[-1]))
                            
                    for dim in alarm.get('Dimensions', []):
                        if dim['Name'] == 'InstanceId':
                            dependencies.append(ResourceDependency(type='EC2', id=dim['Value']))
                        elif dim['Name'] == 'TableName':
                            dependencies.append(ResourceDependency(type='DynamoDBTable', id=dim['Value']))
                        elif dim['Name'] == 'FunctionName':
                            dependencies.append(ResourceDependency(type='Lambda', id=dim['Value']))
                            
                    res = NormalizedResource(
                        resource_id=alarm_arn,
                        resource_type='CloudWatchAlarm',
                        region=region,
                        name=alarm_name,
                        status=alarm.get('StateValue', 'Unknown'),
                        metadata={
                            'arn': alarm_arn,
                            'description': alarm.get('AlarmDescription', ''),
                            'namespace': alarm.get('Namespace', ''),
                            'metric_name': alarm.get('MetricName', '')
                        },
                        configuration={
                            'statistic': alarm.get('Statistic', ''),
                            'period': alarm.get('Period', 0),
                            'evaluation_periods': alarm.get('EvaluationPeriods', 0),
                            'threshold': alarm.get('Threshold', 0.0),
                            'comparison_operator': alarm.get('ComparisonOperator', ''),
                            'dimensions': alarm.get('Dimensions', [])
                        },
                        tags={},
                        dependencies=dependencies
                    )
                    resources.append(res.dict())
        except Exception:
            logger.exception('CloudWatch discovery failed for region %s', region)
        return resources

class CloudWatchMetrics:
    @staticmethod
    def get_ec2_cpu(
        cloud_account_id: int,
        instance_id: str
    ) -> Optional[float]:
        try:
            client = get_aws_client(
                "cloudwatch",
                cloud_account_id
            )

            end_time = datetime.datetime.utcnow()

            start_time = (
                end_time -
                datetime.timedelta(hours=1)
            )

            response = client.get_metric_statistics(
                Namespace="AWS/EC2",

                MetricName="CPUUtilization",

                Dimensions=[
                    {
                        "Name": "InstanceId",
                        "Value": instance_id
                    }
                ],

                StartTime=start_time,

                EndTime=end_time,

                Period=300,

                Statistics=["Average"]
            )

            datapoints = response.get("Datapoints", [])

            if not datapoints:
                logger.warning(
                    "CloudWatch unavailable for %s: no CPU datapoints returned.",
                    instance_id,
                )
                return None

            latest = sorted(
                datapoints,
                key=lambda x: x["Timestamp"]
            )[-1]

            return round(
                latest["Average"],
                2
            )
        except Exception as error:
            logger.warning(
                "CloudWatch unavailable for %s: %s",
                instance_id,
                error,
            )
            return None
