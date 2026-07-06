import boto3
import logging
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
                    resources.append({'resource_id': api_id, 'resource_type': 'APIGateway', 'region': region, 'name': api.get('name'), 'provider': 'AWS', 'metadata': {'protocol': 'REST', 'endpoint': f'https://{api_id}.execute-api.{region}.amazonaws.com', 'description': api.get('description', ''), 'created_at': str(api.get('createdDate', '')), 'endpoint_configuration': api.get('endpointConfiguration', {}).get('types', []), 'tags': api.get('tags', {})}, 'dependencies': []})
                    try:
                        stages_resp = client.get_stages(restApiId=api_id)
                        for stage in stages_resp.get('item', []):
                            stage_name = stage['stageName']
                            resources.append({'resource_id': f'{api_id}/{stage_name}', 'resource_type': 'APIGatewayStage', 'region': region, 'name': f"{api.get('name')}/{stage_name}", 'provider': 'AWS', 'metadata': {'api_id': api_id, 'stage_name': stage_name, 'deployment_id': stage.get('deploymentId', ''), 'invoke_url': f'https://{api_id}.execute-api.{region}.amazonaws.com/{stage_name}', 'logging_level': stage.get('defaultRouteSettings', {}).get('loggingLevel', 'OFF'), 'cache_enabled': stage.get('cacheClusterEnabled', False)}, 'dependencies': []})
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
                    resources.append({'resource_id': api_id, 'resource_type': 'APIGateway', 'region': region, 'name': api.get('Name'), 'provider': 'AWS', 'metadata': {'protocol': api.get('ProtocolType', 'HTTP'), 'endpoint': api.get('ApiEndpoint', ''), 'description': api.get('Description', ''), 'created_at': str(api.get('CreatedDate', '')), 'cors_configuration': api.get('CorsConfiguration', {}), 'tags': api.get('Tags', {})}, 'dependencies': []})
                    try:
                        integ_paginator = client_v2.get_paginator('get_integrations')
                        for integ_page in integ_paginator.paginate(ApiId=api_id):
                            for integ in integ_page.get('Items', []):
                                resources.append({'resource_id': integ['IntegrationId'], 'resource_type': 'APIGatewayIntegration', 'region': region, 'name': f"{api.get('Name')}-{integ.get('IntegrationMethod', 'ANY')}", 'provider': 'AWS', 'metadata': {'api_id': api_id, 'integration_type': integ.get('IntegrationType'), 'integration_uri': integ.get('IntegrationUri', ''), 'payload_format': integ.get('PayloadFormatVersion', '')}, 'dependencies': []})
                    except Exception:
                        pass
        except Exception:
            logger.exception('HTTP API discovery failed for region %s', region)
        return resources