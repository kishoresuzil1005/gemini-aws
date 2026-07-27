import logging
from .assistant_models import ExecutionContext, ResolvedQuery
from .resolver.entity_extractor import EntityExtractor
from .resolver.candidate_generator import CandidateGenerator
from .resolver.candidate_scorer import CandidateScorer
from .resolver.candidate_selector import CandidateSelector
from app.services.ai.orchestrator.feature_flag_util import is_enabled

logger = logging.getLogger(__name__)

class QueryResolver:
    """
    Maps natural language to a Target Resource using structured strategies.
    (EntityExtractor -> CandidateGenerator -> CandidateScorer -> CandidateSelector).
    """

    def __init__(self):
        self.extractor = EntityExtractor()
        self.generator = CandidateGenerator()
        self.scorer = CandidateScorer()
        self.selector = CandidateSelector()

    def resolve(self, context: ExecutionContext) -> ResolvedQuery:
        """
        Resolves the target resource from the user message and memory,
        and returns a detailed ResolvedQuery object.
        """
        message = context.user_message
        
        # 1. Extract Entities
        entities = self.extractor.extract(message)
        
        # 2. Check Conversation Memory
        if entities.get("pronouns") and context.identifier:
            result = ResolvedQuery(
                identifier=context.identifier,
                confidence=0.8,
                source="conversation_memory",
                suggestions=[],
                ambiguity=False,
                matched_resource=None
            )
            logger.info(f"Resolved target resource: {result.identifier} via {result.source}")
            return result
            
        # 3. Generate Candidates
        candidates = self.generator.generate(entities)
        
        # 4. Score Candidates
        scored_candidates = self.scorer.score(candidates, entities)
        
        # 5. Select Best Candidate
        result = self.selector.select(scored_candidates)
        
        if result.identifier:
            logger.info(f"Resolved target resource: {result.identifier} via {result.source}")
        elif result.ambiguity:
            logger.info(f"Ambiguous target resource resolved. Suggestions: {result.suggestions}")
        else:
            logger.info("No specific target resource resolved from the query.")

        return result
