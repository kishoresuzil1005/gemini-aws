from typing import List, Dict, Any
import yaml
import os
import logging

logger = logging.getLogger(__name__)

class CandidateScorer:
    """Scores candidate resources against the extracted entities using YAML rules."""
    
    def __init__(self):
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        config_path = os.path.join(os.path.dirname(__file__), "candidate_scoring.yaml")
        try:
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load candidate_scoring.yaml: {e}")
            # Fallback configuration
            return {
                "exact_id": 99,
                "exact_name": 95,
                "inventory": 90,
                "fuzzy": 70,
                "neo4j": 80,
                "penalties": {}
            }

    def score(self, candidates: List[Dict[str, Any]], entities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Assigns a confidence score (0.0 - 1.0) to each candidate based on YAML rules.
        """
        resource_ids = [rid.lower() for rid in entities.get("resource_ids", [])]
        keywords = [kw.lower() for kw in entities.get("keywords", [])]
        
        scored_candidates = []
        for candidate in candidates:
            score = 0
            
            c_id = (candidate.get("id") or "").lower()
            c_name = (candidate.get("name") or "").lower()
            c_type_raw = candidate.get("type") or []
            if isinstance(c_type_raw, str):
                c_type_raw = [c_type_raw]
            c_types = [t.lower() for t in c_type_raw]
            source = candidate.get("source", "fuzzy")
            
            # Base score from source
            if c_id in resource_ids:
                score = self.config.get("exact_id", 99)
            elif c_name in keywords:
                score = self.config.get("exact_name", 95)
            elif source == "postgres":
                score = self.config.get("inventory", 90)
            elif source == "tag_store":
                score = self.config.get("tag", 88)
            elif source == "neo4j":
                score = self.config.get("neo4j", 80)
            else:
                score = self.config.get("fuzzy", 70)
            
            # Additional matching for fuzzy cases
            if source not in ["postgres", "neo4j"] and keywords:
                matches = sum(1 for kw in keywords if kw in c_name or kw in c_id)
                if matches > 0:
                    score = max(score, self.config.get("fuzzy", 70) + (matches * 5))
                    
            # Apply penalties (placeholder for more advanced checking)
            # if wrong_type: score -= self.config.get("penalties", {}).get("wrong_resource_type", 0)
            
            # Cap at 100
            score = min(score, 100)
            
            scored_candidates.append({
                **candidate,
                "score": score / 100.0
            })
            
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates
