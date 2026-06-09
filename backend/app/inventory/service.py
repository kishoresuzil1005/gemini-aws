from sqlalchemy.orm import Session
from app.database import ResourceDB
from app.inventory.schemas import ResourceSchema

def get_all_resources(db: Session):
    return db.query(ResourceDB).all()

def get_resources_by_type(db: Session, resource_type: str):
    return db.query(ResourceDB).filter(ResourceDB.resource_type == resource_type).all()
