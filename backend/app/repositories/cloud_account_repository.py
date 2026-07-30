from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import CloudAccountDB
from app.repositories.base import BaseRepository

class CloudAccountRepository(BaseRepository[CloudAccountDB]):
    def __init__(self):
        super().__init__(CloudAccountDB)

    def get_by_provider(self, db: Session, provider: str) -> List[CloudAccountDB]:
        return db.query(self.model).filter(self.model.provider == provider).all()

    def get_all_ordered_by_created_at(self, db: Session) -> List[CloudAccountDB]:
        return db.query(self.model).order_by(self.model.created_at.desc()).all()

cloud_account_repo = CloudAccountRepository()
