import boto3
import logging
from app.providers.aws.models import NormalizedResource, ResourceDependency

logger = logging.getLogger(__name__)

class APIGatewayDiscovery:
    @staticmethod
    def discover(region: str) -> list[dict]:
        resources = []
        try:
            client = boto3.client('apigateway', region_name=region)
            paginator = client.get_paginator('get_rest_apis')
            for page in paginator.paginate():
                for api in page.get('items', []):
                    api_id = api['id']
                    
                    tags = api.get('tags', {})
                    
                    dependencies = []
                    
                    res = NormalizedResource(
                        resource_id=api_id,
                        resource_type='APIGateway',
                        region=region,
                        name=api.get('name'),
                        status='Active',
                        metadata={
                            'protocol': 'REST',
                            'endpoint': f'https://{api_id}.execute-api.{region}.amazonaws.com',
                            'description': api.get('description', ''),
                            'created_at': str(api.get('createdDate', ''))
                        },
                        configuration={
                            'endpoint_configuration': api.get('endpointConfiguration', {}).get('types', [])
                        },
                        tags=tags,
                        dependencies=dependencies
                    )
                    resources.append(res.dict())
                    
                    try:
                        stages_resp = client.get_stages(restApiId=api_id)
                        for stage in stages_resp.get('item', []):
                            stage_name = stage['stageName']
                            
                            stage_tags = stage.get('tags', {})
                            
                            stage_dependencies = [ResourceDependency(type='APIGateway', id=api_id)]
                            web_acl_arn = stage.get('webAclArn')
                            if web_acl_arn:
                                stage_dependencies.append(ResourceDependency(type='WAFWebACL', id=web_acl_arn))
                                
                            stage_res = NormalizedResource(
                                resource_id=f'{api_id}/{stage_name}',
                                resource_type='APIGatewayStage',
                                region=region,
                                name=f"{api.get('name')}/{stage_name}",
                                status='Active',
                                metadata={
                                    'api_id': api_id,
                                    'stage_name': stage_name,
                                    'deployment_id': stage.get('deploymentId', ''),
                                    'invoke_url': f'https://{api_id}.execute-api.{region}.amazonaws.com/{stage_name}'
                                },
                                security={
                                    'web_acl_arn': web_acl_arn
                                },
                                configuration={
                                    'logging_level': stage.get('defaultRouteSettings', {}).get('loggingLevel', 'OFF'),
                                    'cache_enabled': stage.get('cacheClusterEnabled', False)
                                },
                                tags=stage_tags,
                                dependencies=stage_dependencies
                            )
                            resources.append(stage_res.dict())
                    except Exception:
                        pass
        except Exception:
            logger.exception('REST API discovery failed for region %s', region)
            
        try:
            client_v2 = boto3.client('apigatewayv2', region_name=region)
            paginator_v2 = client_v2.get_paginator('get_apis')
            for page in paginator_v2.paginate():
                for api in page.get('Items', []):
                    api_id = api['ApiId']
                    tags = api.get('Tags', {})
                    
                    dependencies = []
                    
                    res_v2 = NormalizedResource(
                        resource_id=api_id,
                        resource_type='APIGateway',
                        region=region,
                        name=api.get('Name'),
                        status='Active',
                        metadata={
                            'protocol': api.get('ProtocolType', 'HTTP'),
                            'endpoint': api.get('ApiEndpoint', ''),
                            'description': api.get('Description', ''),
                            'created_at': str(api.get('CreatedDate', ''))
                        },
                        configuration={
                            'cors_configuration': api.get('CorsConfiguration', {})
                        },
                        tags=tags,
                        dependencies=dependencies
                    )
                    resources.append(res_v2.dict())
                    
                    try:
                        integ_paginator = client_v2.get_paginator('get_integrations')
                        for integ_page in integ_paginator.paginate(ApiId=api_id):
                            for integ in integ_page.get('Items', []):
                                integ_id = integ['IntegrationId']
                                
                                integ_dependencies = [ResourceDependency(type='APIGateway', id=api_id)]
                                integ_uri = integ.get('IntegrationUri', '')
                                if ':lambda:' in integ_uri:
                                    # Very basic heuristic to grab Lambda ARN
                                    try:
                                        lambda_arn = integ_uri.split('function:')[-1].split('/')[0]
                                        integ_dependencies.append(ResourceDependency(type='Lambda', id=lambda_arn))
                                    except Exception:
                                        pass
                                
                                integ_res = NormalizedResource(
                                    resource_id=integ_id,
                                    resource_type='APIGatewayIntegration',
                                    region=region,
                                    name=f"{api.get('Name')}-{integ.get('IntegrationMethod', 'ANY')}",
                                    status='Active',
                                    metadata={
                                        'api_id': api_id,
                                        'integration_type': integ.get('IntegrationType'),
                                        'integration_uri': integ_uri,
                                        'payload_format': integ.get('PayloadFormatVersion', '')
                                    },
                                    configuration={},
                                    tags={},
                                    dependencies=integ_dependencies
                                )
                                resources.append(integ_res.dict())
                    except Exception:
                        pass
        except Exception:
            logger.exception('HTTP API discovery failed for region %s', region)
        return resources