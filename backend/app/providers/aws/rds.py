import boto3

class RDSDiscovery:

    @staticmethod
    def discover(region):
        try:
            client = boto3.client('rds', region_name=region)
            response = client.describe_db_instances()
            rds_instances = []
            for db in response.get('DBInstances', []):
                rds_instances.append({'resource_id': db['DBInstanceIdentifier'], 'resource_type': 'RDS', 'region': region, 'status': db.get('DBInstanceStatus'), 'provider': 'AWS', 'metadata': {'engine': db.get('Engine'), 'class': db.get('DBInstanceClass'), 'multi_az': db.get('MultiAZ', False), 'vpc_security_groups': db.get('VpcSecurityGroups', []), 'subnet_group': db.get('DBSubnetGroup', {})}, 'dependencies': ([{'type': 'VPC', 'id': db.get('DBSubnetGroup', {}).get('VpcId')}] if db.get('DBSubnetGroup', {}).get('VpcId') else [])})
            return rds_instances
        except Exception:
            return []