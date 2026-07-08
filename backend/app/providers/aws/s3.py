import boto3
import concurrent.futures
from typing import List
from botocore.exceptions import ClientError
from app.providers.aws.models import NormalizedResource

class S3Discovery:
    @staticmethod
    def _get_bucket_config(bucket_name: str) -> NormalizedResource:
        # Create thread-local client
        client = boto3.client('s3')
        
        tags = {}
        versioning = "Disabled"
        encryption = None
        pab = {}
        logging = {}
        lifecycle = []
        website = {}
        
        try:
            # Tags
            try:
                tags_resp = client.get_bucket_tagging(Bucket=bucket_name)
                tags = {t['Key']: t['Value'] for t in tags_resp.get('TagSet', [])}
            except ClientError as e:
                pass
                
            # Versioning
            try:
                vers_resp = client.get_bucket_versioning(Bucket=bucket_name)
                versioning = vers_resp.get('Status', 'Disabled')
            except ClientError:
                pass
                
            # Encryption
            try:
                enc_resp = client.get_bucket_encryption(Bucket=bucket_name)
                rules = enc_resp.get('ServerSideEncryptionConfiguration', {}).get('Rules', [])
                if rules:
                    encryption = rules[0].get('ApplyServerSideEncryptionByDefault', {})
            except ClientError:
                pass
                
            # Public Access Block
            try:
                pab_resp = client.get_public_access_block(Bucket=bucket_name)
                pab = pab_resp.get('PublicAccessBlockConfiguration', {})
            except ClientError:
                pass
                
            # Logging
            try:
                log_resp = client.get_bucket_logging(Bucket=bucket_name)
                logging = log_resp.get('LoggingEnabled', {})
            except ClientError:
                pass
                
            # Lifecycle
            try:
                lc_resp = client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
                lifecycle = lc_resp.get('Rules', [])
            except ClientError:
                pass
                
            # Website
            try:
                web_resp = client.get_bucket_website(Bucket=bucket_name)
                website = {'index_document': web_resp.get('IndexDocument'), 'error_document': web_resp.get('ErrorDocument')}
            except ClientError:
                pass
                
        except Exception as e:
            print(f"Error fetching configs for {bucket_name}: {e}")

        res = NormalizedResource(
            resource_id=bucket_name,
            resource_type='S3',
            region='global', # S3 bucket list is global, location constraint could be fetched
            name=bucket_name,
            status='Active',
            metadata={},
            security={
                'encryption': encryption,
                'public_access_block': pab
            },
            configuration={
                'versioning': versioning,
                'lifecycle_rules': len(lifecycle),
                'website_hosting': website
            },
            monitoring={
                'logging': logging
            },
            tags=tags,
            dependencies=[]
        )
        return res

    @staticmethod
    def discover(region: str = None) -> List[dict]:
        try:
            client = boto3.client('s3')
            response = client.list_buckets()
            bucket_names = [b['Name'] for b in response.get('Buckets', [])]
            
            resources = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = {executor.submit(S3Discovery._get_bucket_config, name): name for name in bucket_names}
                for future in concurrent.futures.as_completed(futures):
                    try:
                        res = future.result()
                        resources.append(res.dict())
                    except Exception as e:
                        print(f"Error processing bucket {futures[future]}: {e}")
                        
            return resources
        except Exception as e:
            print(f"Error in S3Discovery: {e}")
            return []