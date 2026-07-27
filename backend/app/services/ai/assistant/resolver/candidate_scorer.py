from typing import List, Dict, Any

class CandidateScorer:
    """Scores candidate resources against the extracted entities."""
    
    def score(self, candidates: List[Dict[str, Any]], entities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Assigns a confidence score (0.0 - 1.0) to each candidate.
        Candidates are returned sorted by score descending.
        """
        resource_ids = entities.get("resource_ids", [])
        keywords = entities.get("keywords", [])
        
        scored_candidates = []
        for candidate in candidates:
            score = 0.0
            
            c_id = (candidate.get("id") or "").lower()
            c_name = (candidate.get("name") or "").lower()
            c_type_raw = candidate.get("type") or []
            if isinstance(c_type_raw, str):
                c_type_raw = [c_type_raw]
            c_types = [t.lower() for t in c_type_raw]
            
            # 1. Exact ID Match (Highest confidence)
            if any(rid.lower() == c_id for rid in resource_ids):
                score = 0.99
                
            # 2. Keyword matching
            elif keywords:
                matches = 0
                for kw in keywords:
                    kw_lower = kw.lower()
                    
                    # Exact name match gets a huge boost
                    if kw_lower == c_name:
                        matches += 3
                    # Exact type match gets a moderate boost
                    elif kw_lower in c_types:
                        matches += 2
                    # Partial matches
                    elif kw_lower in c_name or kw_lower in c_id:
                        matches += 1
                        
                if matches > 0:
                    # Base score for keyword matching + boost per match
                    score = min(0.60 + (matches * 0.15), 0.95)
            
            scored_candidates.append({
                **candidate,
                "score": score
            })
            
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates
