import logging
import re
from .assistant_models import ExecutionContext, ResolvedQuery
from app.services.graph.neo4j_service import Neo4jService

logger = logging.getLogger(__name__)

class QueryResolver:
    """
    Maps natural language to a Target Resource using structured strategies.
    (Regex/IDs -> Conversation Memory -> DB Lookup).
    """

    _RESOURCE_ID = re.compile(
        r"\b(?:i|vpc|subnet|sg|vol|eni|igw|nat|rtb)-[a-z0-9-]{3,}\b|"
        r"\barn:aws:[^\s,]+\b",
        re.IGNORECASE,
    )

    def resolve(self, context: ExecutionContext) -> ResolvedQuery:
        """
        Resolves the target resource from the user message and memory,
        and returns a detailed ResolvedQuery object.
        """
        message = context.user_message.lower()
        
        result = ResolvedQuery(
            identifier=None,
            confidence=0.0,
            source="none",
            suggestions=[],
            ambiguity=False,
            matched_resource=None
        )

        # Strategy 1: canonical cloud resource IDs and ARNs in the request.
        match = self._RESOURCE_ID.search(message)
        if match:
            result.identifier = match.group(0)
            result.confidence = 0.95
            result.source = "regex"

        # Strategy 2: Conversation Memory
        if not result.identifier and any(word in message for word in ["it", "that", "this"]):
            if context.identifier:
                result.identifier = context.identifier
                result.confidence = 0.8
                result.source = "conversation_memory"

        # Strategy 3: Graph DB lookup (Fallback search)
        if not result.identifier:
            stop_words = {"why", "is", "are", "my", "our", "the", "a", "an", "unhealthy", "failing", "broken", "what", "how", "who", "where", "down", "issue", "problem", "error", "not", "working"}
            words = [re.sub(r'[^a-zA-Z0-9-]', '', w.lower()) for w in message.split()]
            keywords = [w for w in words if w not in stop_words and len(w) > 2]
            
            if keywords:
                try:
                    neo4j = Neo4jService()
                    query = """
                    MATCH (n:Resource)
                    WHERE ANY(word IN $words WHERE 
                        toLower(n.resource_id) CONTAINS word OR 
                        toLower(coalesce(n.name, '')) CONTAINS word OR 
                        toLower(coalesce(n.resource_type, '')) CONTAINS word)
                    RETURN n.resource_id AS id, n.name AS name, n.resource_type AS type
                    LIMIT 5
                    """
                    records = neo4j.query(query, words=keywords)
                    
                    if records:
                        if len(records) == 1:
                            result.identifier = records[0]["id"]
                            result.confidence = 0.8
                            result.source = "db_lookup"
                        else:
                            result.ambiguity = True
                            result.suggestions = [f"- {r['id']} ({r.get('name') or r.get('type', 'Unknown')})" for r in records]
                            result.source = "db_lookup_ambiguous"
                except Exception as e:
                    logger.error(f"Error querying Neo4j in QueryResolver: {e}")
        
        if result.identifier:
            print(f"Resolved Identifier:\n{result.identifier}")
            print(f"Resolved target resource: {result.identifier} via {result.source}")
        elif result.ambiguity:
            print(f"Ambiguous target resource resolved. Suggestions: {result.suggestions}")
        else:
            print("No specific target resource resolved from the query.")

        return result
