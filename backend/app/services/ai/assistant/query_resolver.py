import logging
import re
from .assistant_models import ExecutionContext, ResolvedQuery

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

        # Strategy 3: known resource names. A repository-backed strategy can be
        # injected later without changing the response contract.
        if not result.identifier:
            if "cloudops-db" in message:
                result.identifier = "cloudops-db"
                result.confidence = 0.7
                result.source = "db_lookup"
        
        if result.identifier:
            print(f"Resolved Identifier:\n{result.identifier}")
            print(f"Resolved target resource: {result.identifier} via {result.source}")
        else:
            print("No specific target resource resolved from the query.")

        return result
