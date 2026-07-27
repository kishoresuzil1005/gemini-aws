import logging
from typing import List, Dict, Any
from app.services.graph.neo4j_service import Neo4jService

logger = logging.getLogger(__name__)

class CandidateGenerator:
    """Fetches candidate resources from the graph database using extracted entities."""
    
    def __init__(self):
        self.neo4j = Neo4jService()
        
    def generate(self, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Queries Neo4j for resources matching the extracted IDs or keywords."""
        candidates = []
        
        # 1. Exact ID lookup
        resource_ids = entities.get("resource_ids", [])
        if resource_ids:
            query = """
            MATCH (n:Resource)
            WHERE n.resource_id IN $ids
            RETURN n.resource_id AS id, n.name AS name, n.resource_type AS type
            """
            try:
                records = self.neo4j.query(query, ids=resource_ids)
                candidates.extend([dict(r) for r in records])
            except Exception as e:
                logger.error(f"Error querying Neo4j in CandidateGenerator (IDs): {e}")
                
            # If we found exact matches, we might just return them, 
            # but we can also gather keyword matches and let scorer decide.
            
        # 2. Keyword lookup (Fuzzy match)
        keywords = entities.get("keywords", [])
        if keywords:
            # We match if ANY keyword matches id, name, or type. Scorer will refine.
            query = """
            MATCH (n:Resource)
            WHERE ANY(word IN $words WHERE 
                toLower(n.resource_id) CONTAINS word OR 
                toLower(coalesce(n.name, '')) CONTAINS word OR 
                toLower(coalesce(n.resource_type, '')) CONTAINS word)
            RETURN n.resource_id AS id, n.name AS name, n.resource_type AS type
            LIMIT 15
            """
            try:
                records = self.neo4j.query(query, words=keywords)
                # Avoid duplicates if ID matched already
                existing_ids = {c["id"] for c in candidates}
                for r in records:
                    if r["id"] not in existing_ids:
                        candidates.append(dict(r))
            except Exception as e:
                logger.error(f"Error querying Neo4j in CandidateGenerator (Keywords): {e}")
                
        return candidates
