import re
from typing import List, Dict, Any

class RetrievalOptimizer:
    def __init__(self, min_score: float = 0.65):
        self.min_score = min_score

    def optimize(self, query: str, matches: List[Dict[str, Any]], final_k: int = 8) -> Dict[str, Any]:
        stats = {
            "retrieved": len(matches),
            "filtered": 0,
            "duplicates_removed": 0,
            "reranked": 0,
            "used": 0
        }
        
        # 1. Similarity Filtering
        filtered_matches = []
        for m in matches:
            if m.get("score", 0.0) >= self.min_score and m.get("payload", {}).get("content", "").strip():
                filtered_matches.append(m)
                
        stats["filtered"] = len(filtered_matches)
        
        # 2. Duplicate Removal
        unique_matches = []
        seen_content_hashes = set()
        for m in filtered_matches:
            content = m.get("payload", {}).get("content", "").strip()
            # Simple hash based on first 100 chars to catch near duplicates
            content_hash = hash(content[:100]) 
            if content_hash not in seen_content_hashes:
                seen_content_hashes.add(content_hash)
                unique_matches.append(m)
            else:
                stats["duplicates_removed"] += 1
                
        # 3. Keyword and Category Boosting
        query_terms = set(re.findall(r'\w+', query.lower()))
        
        for m in unique_matches:
            content = m.get("payload", {}).get("content", "").lower()
            metadata = m.get("payload", {}).get("metadata", {})
            source = metadata.get("source", "").lower()
            
            boost = 0.0
            
            # Keyword boosting
            for term in query_terms:
                if len(term) > 3 and term in content:
                    boost += 0.02
                    
            # Category/Source boosting based on query terms
            for term in query_terms:
                if len(term) > 3 and term in source:
                    boost += 0.05
                    
            m["rerank_score"] = m.get("score", 0.0) + boost
            
        # Sort by new reranked score
        unique_matches.sort(key=lambda x: x.get("rerank_score", 0.0), reverse=True)
        stats["reranked"] = len(unique_matches)
        
        # 4. Diversity Selection & Top K
        final_selection = []
        seen_sources = set()
        
        # First pass: try to get diverse sources
        for m in unique_matches:
            if len(final_selection) >= final_k:
                break
                
            source = m.get("payload", {}).get("metadata", {}).get("source", "Unknown")
            if source not in seen_sources:
                seen_sources.add(source)
                final_selection.append(m)
                
        # Second pass: fill remaining slots if needed
        if len(final_selection) < final_k:
            for m in unique_matches:
                if len(final_selection) >= final_k:
                    break
                if m not in final_selection:
                    final_selection.append(m)
                    
        stats["used"] = len(final_selection)
        
        return {
            "optimized_chunks": final_selection,
            "stats": stats
        }
