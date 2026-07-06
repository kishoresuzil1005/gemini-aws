import boto3
import logging
logger = logging.getLogger(__name__)

class RouteTableDiscovery:

    @staticmethod
    def discover(region):
        try:
            client = boto3.client('ec2', region_name=region)
            
            # Fetch all subnets in this region to resolve implicit main route table associations
            subnets_by_vpc = {}
            try:
                subnet_paginator = client.get_paginator('describe_subnets')
                for page in subnet_paginator.paginate():
                    for subnet in page.get('Subnets', []):
                        vpc_id = subnet.get('VpcId')
                        if vpc_id not in subnets_by_vpc:
                            subnets_by_vpc[vpc_id] = []
                        subnets_by_vpc[vpc_id].append(subnet.get('SubnetId'))
            except Exception as e:
                logger.error(f"Failed to fetch subnets for implicit route associations: {e}")

            paginator = client.get_paginator('describe_route_tables')
            route_tables_data = []
            
            # First pass: collect all explicit associations to know which subnets are covered
            explicitly_associated_subnets = set()
            raw_route_tables = []
            
            for page in paginator.paginate():
                for rt in page.get('RouteTables', []):
                    raw_route_tables.append(rt)
                    for assoc in rt.get('Associations', []):
                        if assoc.get('SubnetId'):
                            explicitly_associated_subnets.add(assoc.get('SubnetId'))

            # Second pass: process route tables and apply implicit associations
            route_tables = []
            for rt in raw_route_tables:
                vpc_id = rt.get('VpcId')
                associations = [assoc.get('SubnetId') for assoc in rt.get('Associations', []) if assoc.get('SubnetId')]
                
                is_main = any(assoc.get('Main') for assoc in rt.get('Associations', []))
                
                # If this is the main route table for the VPC, find all subnets in the VPC
                # that DO NOT have an explicit association, and implicitly associate them here.
                if is_main and vpc_id in subnets_by_vpc:
                    for subnet_id in subnets_by_vpc[vpc_id]:
                        if subnet_id not in explicitly_associated_subnets and subnet_id not in associations:
                            associations.append(subnet_id)
                
                gateways = []
                nat_gateways = []
                for route in rt.get('Routes', []):
                    if route.get('GatewayId'):
                        gateways.append(route['GatewayId'])
                    if route.get('NatGatewayId'):
                        nat_gateways.append(route['NatGatewayId'])
                        
                route_tables.append({
                    'resource_id': rt['RouteTableId'], 
                    'resource_type': 'RouteTable', 
                    'region': region, 
                    'name': rt['RouteTableId'], 
                    'provider': 'AWS', 
                    'metadata': {
                        'vpc_id': vpc_id, 
                        'subnets': associations, 
                        'internet_gateways': gateways, 
                        'nat_gateways': nat_gateways, 
                        'route_count': len(rt.get('Routes', [])),
                        'is_main': is_main
                    }, 
                    'dependencies': (
                        ([{'type': 'VPC', 'id': vpc_id}] if vpc_id else []) + 
                        [{'type': 'Subnet', 'id': s} for s in associations] + 
                        [{'type': 'InternetGateway', 'id': g} for g in gateways] + 
                        [{'type': 'NatGateway', 'id': n} for n in nat_gateways]
                    )
                })
            return route_tables
        except Exception:
            logger.exception('Route Table discovery failed for region %s', region)
            return []
