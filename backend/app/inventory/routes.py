from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.inventory import service, schemas

router = APIRouter()

# @router.get("/resources")
# def get_resources(db: Session = Depends(get_db)):
    # return service.get_all_resources(db)

@router.get("/resources/compute")
def get_compute_resources(db: Session = Depends(get_db)):
    # e.g., Filter for EC2 or EKS resources
    return service.get_resources_by_type(db, "EC2")

@router.get("/resources/databases")
def get_database_resources(db: Session = Depends(get_db)):
    return service.get_resources_by_type(db, "RDS")
