from typing import List, Dict, Any
from app.services.ai.assistant.assistant_models import ResolvedQuery

class CandidateSelector:
    """Evaluates scored candidates and constructs the final ResolvedQuery."""
    
    def __init__(self, ambiguity_threshold: float = 0.15, min_confidence: float = 0.70, auto_select_threshold: float = 0.95, best_candidate_threshold: float = 0.80):
        self.ambiguity_threshold = ambiguity_threshold
        self.min_confidence = min_confidence
        self.auto_select_threshold = auto_select_threshold
        self.best_candidate_threshold = best_candidate_threshold

    def select(self, scored_candidates: List[Dict[str, Any]]) -> ResolvedQuery:
        """
        Selects the best candidate or returns an ambiguous/not-found result.
        """
        result = ResolvedQuery(
            identifier=None,
            confidence=0.0,
            source="none",
            suggestions=[],
            ambiguity=False,
            not_found=False,
            matched_resource=None
        )
        
        # If there are keywords/IDs but no candidates returned, it's not found
        if not scored_candidates:
            result.not_found = True
            return result
            
        top_candidate = scored_candidates[0]
        top_score = top_candidate["score"]
        
        if top_score < self.min_confidence:
            result.not_found = True
            return result
            
        if top_score >= self.auto_select_threshold:
            result.identifier = top_candidate["id"]
            result.confidence = top_score
            result.source = "candidate_pipeline_exact"
            return result
            
        # >= 80 and < 95 logic
        if top_score >= self.best_candidate_threshold:
            if len(scored_candidates) == 1:
                result.identifier = top_candidate["id"]
                result.confidence = top_score
                result.source = "candidate_pipeline"
                return result
                
            # Check for ambiguity if multiple candidates
            second_candidate = scored_candidates[1]
            second_score = second_candidate["score"]
            
            # If the gap between top and second is smaller than the threshold, it's ambiguous
            if (top_score - second_score) < self.ambiguity_threshold:
                result.ambiguity = True
                result.source = "candidate_pipeline_ambiguous"
                # Get all candidates within the ambiguity threshold of the top score
                ambiguous_candidates = [
                    c for c in scored_candidates 
                    if (top_score - c["score"]) < self.ambiguity_threshold
                ]
                result.suggestions = [
                    f"- {c['id']} ({c.get('name') or c.get('type') or 'Unknown'})" 
                    for c in ambiguous_candidates[:5]
                ]
            else:
                result.identifier = top_candidate["id"]
                result.confidence = top_score
                result.source = "candidate_pipeline"
                
            return result
            
        # Score is between 70 and 80, considered low confidence but valid fallback
        result.identifier = top_candidate["id"]
        result.confidence = top_score
        result.source = "candidate_pipeline_low_confidence"
        return result
