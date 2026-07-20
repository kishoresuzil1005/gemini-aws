import re
from typing import Optional

class ResourceExtractor:
    """
    Production-ready resource extractor.
    Extracts AWS resource IDs or named resources from natural language.
    """
    
    RESOURCE_PATTERNS = [
        r"^i-[a-zA-Z0-9]+$",
        r"^subnet-[a-zA-Z0-9]+$",
        r"^sg-[a-zA-Z0-9]+$",
        r"^rtb-[a-zA-Z0-9]+$",
        r"^vpc-[a-zA-Z0-9]+$",
        r"^igw-[a-zA-Z0-9]+$",
        r"^eni-[a-zA-Z0-9]+$",
        r"^nat-[a-zA-Z0-9]+$",
        r"^vol-[a-zA-Z0-9]+$",
        r"^snap-[a-zA-Z0-9]+$",
        r"^alb-[a-zA-Z0-9]+$",
        r"^arn:.*"
    ]

    RESERVED_WORDS = {
        "what", "why", "how", "depends", "dependency", "dependencies", "show", "delete", 
        "remove", "move", "execute", "generate", "terraform", "cloudformation", 
        "recommend", "please", "tell", "can", "could", "would", "should", 
        "does", "did", "is", "are", "be", "into", "from", "with", "using", 
        "safe", "safely", "analyze", "analyse", "check", "inspect", "review",
        "automation", "automate", "orchestrate", "rollback", "remediate", 
        "explain", "describe", "compare", "about", "inventory",
        "the", "of", "a", "an", "and", "to", "for", "in", "on", "at",
        "breaks", "fails", "fail", "happens", "if"
    }

    def extract(self, message: str) -> Optional[str]:
        target_resource = None
        tokens = re.findall(r"[A-Za-z0-9_.:/-]+", message)

        # 1. Exact AWS IDs
        for token in tokens:
            for pattern in self.RESOURCE_PATTERNS:
                if re.match(pattern, token):
                    target_resource = token
                    break
            if target_resource:
                break

        # 2. Named Resource (Fallback)
        if target_resource is None:
            for token in tokens:
                lower = token.lower()
                if lower in self.RESERVED_WORDS:
                    continue
                if len(token) < 3:
                    continue
                target_resource = token
                break
        if target_resource:
            target_resource = target_resource.rstrip(".,;:!?")

        return target_resource