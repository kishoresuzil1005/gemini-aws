import boto3
from app.database import SessionLocal, CloudAccountDB

def get_aws_client(service, cloud_account_id, region="us-east-1"):
    db = SessionLocal()
    account = db.query(CloudAccountDB).filter(CloudAccountDB.id == cloud_account_id).first()
    db.close()
    
    if not account:
        raise Exception("Cloud account not found")

    # In production, use STS AssumeRole using account.role_arn
    # For now, using default credentials + region override
    return boto3.client(service, region_name=account.region)
