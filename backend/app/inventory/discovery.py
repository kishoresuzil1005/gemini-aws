from sqlalchemy.orm import Session
from app.database import ResourceDB, CloudAccountDB
from app.providers.aws.ec2 import EC2Adapter
from app.providers.aws.rds import RDSAdapter
from app.providers.aws.s3 import S3Adapter

def discover_resources(db: Session, cloud_account_id: int):
    account = db.query(CloudAccountDB).filter(CloudAccountDB.id == cloud_account_id).first()
    if not account or account.provider != "AWS":
        return

    # Initialize Adapters
    ec2 = EC2Adapter(cloud_account_id)
    rds = RDSAdapter(cloud_account_id)
    s3 = S3Adapter(cloud_account_id)
    
    # Discovery Logic (Simplified)
    resources = []
    
    # EC2 Instances
    instances = ec2.describe_instances()
    for reservation in instances.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            resources.append(ResourceDB(
                cloud_account_id=cloud_account_id,
                provider="AWS",
                resource_type="EC2",
                resource_id=instance["InstanceId"],
                name=instance.get("Tags", [{}])[0].get("Value", "Unknown"),
                status=instance["State"]["Name"]
            ))

    # Save to DB (Clear old first - Reconciliation step)
    db.query(ResourceDB).filter(ResourceDB.cloud_account_id == cloud_account_id).delete()
    db.add_all(resources)
    db.commit()
