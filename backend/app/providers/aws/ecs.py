import boto3
import logging
from app.providers.aws.models import NormalizedResource, ResourceDependency

logger = logging.getLogger(__name__)

class ECSDiscovery:
    @staticmethod
    def discover(region: str):
        try:
            client = boto3.client('ecs', region_name=region)
            response = client.list_clusters()
            clusters = []
            
            for arn in response.get('clusterArns', []):
                name = arn.split('/')[-1]
                
                tags = {}
                try:
                    tags_resp = client.list_tags_for_resource(resourceArn=arn)
                    tags = {t['key']: t['value'] for t in tags_resp.get('tags', [])}
                except Exception: pass
                
                dependencies = []
                services = []
                try:
                    svc_paginator = client.get_paginator('list_services')
                    for page in svc_paginator.paginate(cluster=arn):
                        for svc_arn in page.get('serviceArns', []):
                            services.append(svc_arn)
                except Exception: pass
                
                cluster_info = {}
                try:
                    desc = client.describe_clusters(clusters=[arn], include=['ATTACHMENTS', 'SETTINGS', 'STATISTICS'])
                    if desc.get('clusters'):
                        c_data = desc['clusters'][0]
                        cluster_info = {
                            'status': c_data.get('status'),
                            'registered_container_instances_count': c_data.get('registeredContainerInstancesCount', 0),
                            'running_tasks_count': c_data.get('runningTasksCount', 0),
                            'pending_tasks_count': c_data.get('pendingTasksCount', 0),
                            'active_services_count': c_data.get('activeServicesCount', 0),
                            'statistics': c_data.get('statistics', []),
                            'settings': c_data.get('settings', [])
                        }
                except Exception: pass
                
                res = NormalizedResource(
                    resource_id=arn,
                    resource_type='ECSCluster',
                    region=region,
                    name=name,
                    status=cluster_info.get('status', 'Active'),
                    metadata={
                        'arn': arn,
                        'registered_container_instances': cluster_info.get('registered_container_instances_count', 0),
                        'active_services_count': cluster_info.get('active_services_count', 0)
                    },
                    configuration={
                        'running_tasks': cluster_info.get('running_tasks_count', 0),
                        'pending_tasks': cluster_info.get('pending_tasks_count', 0),
                        'services': services,
                        'settings': cluster_info.get('settings', [])
                    },
                    tags=tags,
                    dependencies=dependencies
                )
                clusters.append(res.dict())
                
            return clusters
        except Exception:
            logger.exception('ECS discovery failed for region %s', region)
            return []