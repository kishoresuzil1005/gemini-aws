import re
from typing import Dict, Any

class IntentClassifier:
    def classify(self, message: str) -> Dict[str, Any]:
        msg_lower = message.lower()
        
        intent = "UNKNOWN"
        target_resource = None
        
        # Simple extraction of a resource id
        words = message.split()
        for word in words:
            word_clean = re.sub(r'[^a-zA-Z0-9-]', '', word)
            if word_clean in ["hello-api", "cloudops-db"] or word_clean.startswith("i-") or word_clean.startswith("subnet-") or word_clean.startswith("rtb-"):
                target_resource = word_clean
                
        if "insecure" in msg_lower or "public" in msg_lower or "security" in msg_lower or "secure" in msg_lower:
            intent = "SECURITY"
        elif "failing" in msg_lower or "why" in msg_lower or "root cause" in msg_lower:
            intent = "ROOT_CAUSE"
        elif "depends" in msg_lower or "dependencies" in msg_lower:
            intent = "DEPENDENCY"
        elif "blast radius" in msg_lower or "what happens if" in msg_lower:
            intent = "BLAST_RADIUS"
        elif "terraform" in msg_lower or "remediate" in msg_lower or "fix" in msg_lower:
            intent = "REMEDIATION"
        elif "automate" in msg_lower or "execute" in msg_lower or "safely" in msg_lower:
            intent = "ORCHESTRATION"
        elif "recommend" in msg_lower or "how do i" in msg_lower:
            intent = "RECOMMENDATION"
        elif "what is" in msg_lower or "documentation" in msg_lower:
            intent = "DOCUMENTATION"
        elif "inventory" in msg_lower or "compare" in msg_lower or "show" in msg_lower:
            intent = "INVENTORY"
            
        return {
            "intent": intent,
            "target_resource": target_resource
        }
