from typing import Dict, Any, List

class ResponseFormatter:
    def __init__(self):
        pass

    def format_response(self, 
                        answer: str, 
                        intent: str, 
                        resource: str,
                        evidence: List[str], 
                        sources: List[str], 
                        confidence: int, 
                        tools_used: List[str]) -> Dict[str, Any]:
        """
        Produces consistent, engineer-friendly responses as described in Phase 5.
        """
        response = {
            "answer": answer,
            "summary": {
                "intent": intent,
                "resource": resource
            },
            "evidence": evidence,
            "sources": sources,
            "confidence": confidence,
            "tools_used": tools_used
        }
        
        return response
