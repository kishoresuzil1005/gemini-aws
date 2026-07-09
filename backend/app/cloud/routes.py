from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.models.core import CloudAccountDB
from app.cloud.schemas import AwsConnectRequest
from app.cloud.aws_service import AwsService
from app.services.aws.region_service import AWSRegionService

try:
    from app.database import SessionLocal, get_db
except ImportError:
    try:
        from app.database.database import SessionLocal, get_db
    except ImportError:
        from ..database import SessionLocal, get_db

router = APIRouter(
    prefix="/api/cloud",
    tags=["Cloud"]
)

@router.post("/aws/connect")
def connect_aws(request: AwsConnectRequest):
    db: Session = SessionLocal()
    try:
        account = CloudAccountDB(
            name=request.account_name,
            provider="AWS",
            region="us-east-1",
            account_id=request.account_id,
            role_arn=request.role_arn,
            credentials_hint=f"External ID: {request.external_id}" if getattr(request, 'external_id', None) else ""
        )
        db.add(account)
        db.commit()
        db.refresh(account)
        return {
            "success": True,
            "account_id": account.id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database insertion failed: {str(e)}")
    finally:
        db.close()

@router.get("/accounts/{account_id}/regions")
def get_regions(account_id: int):
    db: Session = SessionLocal()
    try:
        account = db.query(CloudAccountDB).filter(CloudAccountDB.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="AWS Account not found")
        
        credentials = AwsService.assume_role(
            role_arn=account.role_arn,
            external_id=None # CloudAccountDB does not directly store external_id in a separate column
        )
        regions = AWSRegionService.get_regions(credentials)
        return {
            "success": True,
            "regions": regions
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load assumed regions: {str(e)}")
    finally:
        db.close()
