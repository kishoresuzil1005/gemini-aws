import re
from typing import Dict, Any, List

class EntityExtractor:
    """Extracts entities from user messages for resource resolution."""
    
    _RESOURCE_ID = re.compile(
        r"\b(?:i|vpc|subnet|sg|vol|eni|igw|nat|rtb)-[a-z0-9-]{3,}\b|"
        r"\barn:aws:[^\s,]+\b",
        re.IGNORECASE,
    )
    
    _PRONOUNS = {"it", "that", "this"}
    
    def extract(self, message: str) -> Dict[str, Any]:
        """Extracts resource IDs, pronouns, and keywords from a message."""
        msg_lower = message.lower()
        
        # 1. Exact Resource IDs
        ids = self._RESOURCE_ID.findall(message)
        
        # 2. Pronouns (for conversational memory)
        words = set(re.findall(r'\b\w+\b', msg_lower))
        pronouns = list(words.intersection(self._PRONOUNS))
        
        # 3. Keywords (filtering out stop words)
        stop_words = {"why", "is", "are", "my", "our", "the", "a", "an", "unhealthy", 
                      "failing", "broken", "what", "how", "who", "where", "down", 
                      "issue", "problem", "error", "not", "working", "analyze", 
                      "explain", "show", "me", "details", "about", "this", "that", "it"}
        
        keywords = [w for w in re.sub(r'[^a-zA-Z0-9-_\s]', '', msg_lower).split() 
                    if w not in stop_words and len(w) > 2]
        
        return {
            "resource_ids": ids,
            "pronouns": pronouns,
            "keywords": keywords
        }
