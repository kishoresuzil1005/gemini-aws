import difflib
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import SessionLocal
from app.models.resource import ResourceDB
from app.services.graph.neo4j_service import Neo4jService
from app.services.ai.assistant.assistant_models import ResourceMatch

class ResourceNotFoundError(Exception):
    def __init__(self, resource_id: str, suggestions: List[str]):
        self.resource_id = resource_id
        self.suggestions = suggestions
        super().__init__(f"Resource '{resource_id}' does not exist.")

class ResourceValidator:
    def __init__(self):
        self.neo4j = Neo4jService()

    def resolve(self, candidate: Optional[str], session_id: str = None) -> ResourceMatch:
        """
        Validates a candidate string against PostgreSQL and Neo4j,
        returning a standardized ResourceMatch object with confidence scores.
        """
        match = ResourceMatch()
        
        if not candidate and session_id:
            # Fallback to Conversation Memory
            from app.services.ai.assistant.memory.memory_manager import MemoryManager
            from app.services.ai.assistant.memory.memory_store import MemoryStore
            mm = MemoryManager(MemoryStore())
            ctx = mm.get_context(session_id)
            if ctx and ctx.current_resource:
                candidate = ctx.current_resource
        
        if not candidate:
            return match
            
        db: Session = SessionLocal()
        try:
            # 1. PostgreSQL Lookup
            resource = db.query(ResourceDB).filter(
                or_(ResourceDB.resource_id == candidate, ResourceDB.name == candidate)
            ).first()
            
            if resource:
                match.resource_id = resource.resource_id
                match.resource_name = resource.name
                match.resource_type = resource.resource_type
                match.confidence = 1.0
                match.source = "postgres"
                return match
                
            # 2. Neo4j Lookup
            node = self.neo4j.get_node(resource_id=candidate)
            if node:
                match.resource_id = node.get("id")
                match.resource_name = node.get("name")
                match.resource_type = node.get("type", "Unknown")
                match.confidence = 1.0
                match.source = "neo4j"
                return match
                
            # 3. Fuzzy Search (Suggestions)
            like_matches = db.query(ResourceDB.resource_id).filter(
                ResourceDB.resource_id.ilike(f"%{candidate}%")
            ).limit(3).all()
            
            matches = [m[0] for m in like_matches]
            
            if not matches:
                all_resources = db.query(ResourceDB.resource_id).limit(1000).all()
                all_ids = [m[0] for m in all_resources]
                matches = difflib.get_close_matches(candidate, all_ids, n=3, cutoff=0.4)
                
            match.suggestions = matches
            match.confidence = 0.0
            
        except Exception as e:
            print(f"[ResourceValidator] Resolve failed for {candidate}: {e}")
        finally:
            db.close()
            
        return match
