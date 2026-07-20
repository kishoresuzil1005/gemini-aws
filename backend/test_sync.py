from app.database import get_db
from app.services.graph.graph_sync_service import GraphSyncService
import os
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

db = next(get_db())
sync_service = GraphSyncService(db)
result = sync_service.sync_resources()
print("Sync Result:", result)
