import boto3
import logging
logger = logging.getLogger(__name__)

class RouteTableDiscovery:

    @staticmethod
    def discover(region):
        try:
            client = boto3.client('ec2', region_name=region)
            paginator = client.get_paginator('describe_route_tables')
            route_tables = []
            for page in paginator.paginate():
                for rt in page.get('RouteTables', []):
                    associations = [assoc.get('SubnetId') for assoc in rt.get('Associations', []) if assoc.get('SubnetId')]
                    gateways = []
                    nat_gateways = []
                    for route in rt.get('Routes', []):
                        if route.get('GatewayId'):
                            gateways.append(route['GatewayId'])
                        if route.get('NatGatewayId'):
                            nat_gateways.append(route['NatGatewayId'])
                    route_tables.append({'resource_id': rt['RouteTableId'], 'resource_type': 'RouteTable', 'region': region, 'name': rt['RouteTableId'], 'provider': 'AWS', 'metadata': {'vpc_id': rt.get('VpcId'), 'subnets': associations, 'internet_gateways': gateways, 'nat_gateways': nat_gateways, 'route_count': len(rt.get('Routes', []))}, 'dependencies': ([{'type': 'VPC', 'id': rt.get('VpcId')}] if rt.get('VpcId') else []) + [{'type': 'Subnet', 'id': s} for s in associations] + [{'type': 'InternetGateway', 'id': g} for g in gateways] + [{'type': 'NatGateway', 'id': n} for n in nat_gateways]})
            return route_tables
        except Exception:
            logger.exception('Route Table discovery failed for region %s', region)
            return []