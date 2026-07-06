import re
from typing import Dict, Any

class IntentClassifier:
    def classify(self, message: str) -> Dict[str, Any]:
        """
        In a real LLM implementation, this would use a fast classification prompt.
        For now, we use heuristic keyword matching to determine intent.
        """
        msg_lower = message.lower()
        
        intent = "UNKNOWN"
        target_resource = None
        
        # Simple extraction of a resource id (e.g. hello-api, i-027...)
        words = message.split()
        for word in words:
            word_clean = re.sub(r'[^a-zA-Z0-9-]', '', word)
            if word_clean in ["hello-api", "cloudops-db"] or word_clean.startswith("i-") or word_clean.startswith("subnet-") or word_clean.startswith("rtb-"):
                target_resource = word_clean
                
        if "insecure" in msg_lower or "public" in msg_lower or "security" in msg_lower:
            intent = "SECURITY_ANALYSIS"
        elif "failing" in msg_lower or "why" in msg_lower or "root cause" in msg_lower:
            intent = "ROOT_CAUSE"
        elif "connected" in msg_lower or "dependencies" in msg_lower:
            intent = "DEPENDENCY_ANALYSIS"
        elif "blast radius" in msg_lower:
            intent = "BLAST_RADIUS"
        elif "terraform" in msg_lower or "remediate" in msg_lower or "fix" in msg_lower:
            intent = "REMEDIATION"
        elif "automate" in msg_lower or "execute" in msg_lower or "safely" in msg_lower:
            intent = "ORCHESTRATION"
            
        return {
            "intent": intent,
            "target_resource": target_resource
        }
