import boto3
from app.providers.aws.models import NormalizedResource, ResourceDependency

class IAMDiscovery:
    @staticmethod
    def discover(region: str = 'global') -> list[dict]:
        try:
            client = boto3.client('iam')
            resources = []
            
            # Users
            try:
                user_paginator = client.get_paginator('list_users')
                for page in user_paginator.paginate():
                    for u in page.get('Users', []):
                        tags_resp = client.list_user_tags(UserName=u['UserName'])
                        tags = {t['Key']: t['Value'] for t in tags_resp.get('Tags', [])}
                        
                        dependencies = []
                        policies = []
                        
                        # Inline Policies
                        try:
                            inline_resp = client.list_user_policies(UserName=u['UserName'])
                            policies.extend(inline_resp.get('PolicyNames', []))
                        except Exception: pass
                            
                        # Attached Policies
                        try:
                            attached_resp = client.list_attached_user_policies(UserName=u['UserName'])
                            for pol in attached_resp.get('AttachedPolicies', []):
                                policies.append(pol['PolicyName'])
                                dependencies.append(ResourceDependency(type='IAMPolicy', id=pol['PolicyArn']))
                        except Exception: pass

                        res = NormalizedResource(
                            resource_id=u['Arn'],
                            resource_type='IAMUser',
                            region='global',
                            name=u['UserName'],
                            status='Active',
                            metadata={
                                'created': str(u.get('CreateDate')),
                                'user_id': u.get('UserId'),
                                'path': u.get('Path'),
                                'password_last_used': str(u.get('PasswordLastUsed', ''))
                            },
                            security={
                                'permissions_boundary': u.get('PermissionsBoundary', {}).get('PermissionsBoundaryArn'),
                                'policies': policies
                            },
                            tags=tags,
                            dependencies=dependencies
                        )
                        resources.append(res.dict())
            except Exception: pass

            # Roles
            try:
                role_paginator = client.get_paginator('list_roles')
                for page in role_paginator.paginate():
                    for r in page.get('Roles', []):
                        tags_resp = client.list_role_tags(RoleName=r['RoleName'])
                        tags = {t['Key']: t['Value'] for t in tags_resp.get('Tags', [])}
                        
                        dependencies = []
                        policies = []
                        
                        try:
                            inline_resp = client.list_role_policies(RoleName=r['RoleName'])
                            policies.extend(inline_resp.get('PolicyNames', []))
                        except Exception: pass
                            
                        try:
                            attached_resp = client.list_attached_role_policies(RoleName=r['RoleName'])
                            for pol in attached_resp.get('AttachedPolicies', []):
                                policies.append(pol['PolicyName'])
                                dependencies.append(ResourceDependency(type='IAMPolicy', id=pol['PolicyArn']))
                        except Exception: pass

                        res = NormalizedResource(
                            resource_id=r['Arn'],
                            resource_type='IAMRole',
                            region='global',
                            name=r['RoleName'],
                            status='Active',
                            metadata={
                                'created': str(r.get('CreateDate')),
                                'role_id': r.get('RoleId'),
                                'path': r.get('Path'),
                                'max_session_duration': r.get('MaxSessionDuration')
                            },
                            security={
                                'trust_policy': r.get('AssumeRolePolicyDocument', {}),
                                'permissions_boundary': r.get('PermissionsBoundary', {}).get('PermissionsBoundaryArn'),
                                'policies': policies
                            },
                            tags=tags,
                            dependencies=dependencies
                        )
                        resources.append(res.dict())
            except Exception: pass
            
            return resources
        except Exception:
            return []