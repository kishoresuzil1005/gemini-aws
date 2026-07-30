from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import ResourceDB
from app.repositories.base import BaseRepository

class ResourceRepository(BaseRepository[ResourceDB]):
    def __init__(self):
        super().__init__(ResourceDB)

    def get_by_region(self, db: Session, region: Optional[str] = None) -> List[ResourceDB]:
        query = db.query(self.model)
        if region and region.lower() != "all":
            query = query.filter(self.model.region.ilike(region))
        return query.all()

    def get_by_resource_id(self, db: Session, resource_id: str) -> Optional[ResourceDB]:
        return db.query(self.model).filter(self.model.resource_id == resource_id).first()

resource_repo = ResourceRepository()
