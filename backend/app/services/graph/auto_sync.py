from sqlalchemy.orm import Session
from app.services.graph.graph_sync_service import GraphSyncService

class AutoGraphSync:
    @staticmethod
    def sync(db: Session):
        service = GraphSyncService(db)
        try:
            return service.sync_resources()
        finally:
            service.close()
