import difflib
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.resource import ResourceDB
from app.services.graph.neo4j_service import Neo4jService

class ResourceNotFoundError(Exception):
    def __init__(self, resource_id: str, suggestions: List[str]):
        self.resource_id = resource_id
        self.suggestions = suggestions
        super().__init__(f"Resource '{resource_id}' does not exist.")

class ResourceValidator:
    def __init__(self):
        self.neo4j = Neo4jService()

    def exists(self, resource_id: str) -> bool:
        """
        Check if a resource exists in PostgreSQL or Neo4j.
        """
        if not resource_id:
            return False
            
        # 1. Check PostgreSQL first
        db: Session = SessionLocal()
        try:
            resource = db.query(ResourceDB).filter(ResourceDB.resource_id == resource_id).first()
            if resource:
                return True
        except Exception as e:
            print(f"[ResourceValidator] PostgreSQL check failed for {resource_id}: {e}")
        finally:
            db.close()
            
        # 2. Fallback check in Neo4j
        try:
            node = self.neo4j.get_node(resource_id=resource_id)
            if node:
                return True
        except Exception as e:
            print(f"[ResourceValidator] Neo4j check failed for {resource_id}: {e}")
            
        return False

    def search(self, resource_id: str, limit: int = 3) -> List[str]:
        """
        Attempt to find a similar resource ID if the user made a typo.
        """
        if not resource_id:
            return []
            
        db: Session = SessionLocal()
        try:
            # Simple ILIKE match for partial substrings
            like_matches = db.query(ResourceDB.resource_id).filter(
                ResourceDB.resource_id.ilike(f"%{resource_id}%")
            ).limit(limit).all()
            
            matches = [m[0] for m in like_matches]
            
            # If nothing found, try difflib on a larger subset
            if not matches:
                all_resources = db.query(ResourceDB.resource_id).limit(1000).all()
                all_ids = [m[0] for m in all_resources]
                matches = difflib.get_close_matches(resource_id, all_ids, n=limit, cutoff=0.4)
                
            return matches
        except Exception as e:
            print(f"[ResourceValidator] Search failed: {e}")
            return []
        finally:
            db.close()
