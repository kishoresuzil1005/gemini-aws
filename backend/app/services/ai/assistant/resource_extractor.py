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
        "analyze", "analyse", "check", "review", "inspect", "what", "is", "the",
        "how", "why", "show", "list", "generate", "terraform", "cloudformation",
        "aws", "cli", "execute", "run", "fix", "secure", "security", "recommend",
        "recommendation", "dependency", "blast", "radius", "root", "cause", "remediate",
        "documentation", "inventory", "explain", "describe", "compare", "tell", "me",
        "about", "automation", "automate", "orchestrate", "rollback"
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

        return target_resource
