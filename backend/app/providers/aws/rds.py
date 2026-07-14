import boto3
from app.providers.aws.models import NormalizedResource, ResourceDependency

class RDSDiscovery:
    @staticmethod
    def discover(region: str):
        try:
            client = boto3.client('rds', region_name=region)
            response = client.describe_db_instances()
            rds_instances = []
            
            for db in response.get('DBInstances', []):
                tags_resp = client.list_tags_for_resource(ResourceName=db['DBInstanceArn']) if 'DBInstanceArn' in db else {}
                tags = {tag['Key']: tag['Value'] for tag in tags_resp.get('TagList', [])}
                
                dependencies = []
                
                subnet_group = db.get('DBSubnetGroup', {})
                vpc_id = subnet_group.get('VpcId')
                if vpc_id:
                    dependencies.append(ResourceDependency(type='VPC', id=vpc_id))
                    
                for sub in subnet_group.get('Subnets', []):
                    sub_id = sub.get('SubnetIdentifier')
                    if sub_id:
                        dependencies.append(ResourceDependency(type='Subnet', id=sub_id))
                        
                for sg in db.get('VpcSecurityGroups', []):
                    sg_id = sg.get('VpcSecurityGroupId')
                    if sg_id:
                        dependencies.append(ResourceDependency(type='SecurityGroup', id=sg_id))

                res = NormalizedResource(
                    resource_id=db['DBInstanceIdentifier'],
                    resource_type='RDS',
                    region=region,
                    name=db.get('DBName', db['DBInstanceIdentifier']),
                    status=db.get('DBInstanceStatus', 'Unknown'),
                    metadata={
                        'engine': db.get('Engine'),
                        'engine_version': db.get('EngineVersion'),
                        'class': db.get('DBInstanceClass'),
                        'multi_az': db.get('MultiAZ', False),
                        'storage_type': db.get('StorageType'),
                        'allocated_storage': db.get('AllocatedStorage'),
                        'endpoint': db.get('Endpoint', {}).get('Address'),
                        'port': db.get('Endpoint', {}).get('Port')
                    },
                    security={
                        'storage_encrypted': db.get('StorageEncrypted', False),
                        'kms_key_id': db.get('KmsKeyId'),
                        'iam_database_authentication_enabled': db.get('IAMDatabaseAuthenticationEnabled', False),
                        'vpc_security_groups': [sg.get('VpcSecurityGroupId') for sg in db.get('VpcSecurityGroups', [])]
                    },
                    configuration={
                        'backup_retention_period': db.get('BackupRetentionPeriod'),
                        'db_parameter_groups': [pg.get('DBParameterGroupName') for pg in db.get('DBParameterGroups', [])],
                        'option_group_memberships': [og.get('OptionGroupName') for og in db.get('OptionGroupMemberships', [])],
                        'subnet_group': subnet_group
                    },
                    monitoring={
                        'monitoring_interval': db.get('MonitoringInterval', 0),
                        'performance_insights_enabled': db.get('PerformanceInsightsEnabled', False)
                    },
                    tags=tags,
                    dependencies=dependencies
                )
                rds_instances.append(res.dict())
                
            return rds_instances
        except Exception as e:
            print(f"Error in RDSDiscovery: {e}")
            return []