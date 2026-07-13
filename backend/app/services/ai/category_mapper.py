from typing import List

class CategoryMapper:
    def __init__(self):
        self.CATEGORY_MAP = {
            "architecture": ["architecture", "aws_architecture", "well_architected_framework", "operational_excellence", "reliability", "performance_efficiency", "cost_optimization", "sustainability"],
            "failure": ["disaster_recovery", "reliability", "troubleshooting", "architecture"],
            "production": ["well_architected_framework", "security", "architecture", "operational_excellence"],
            "security": ["security", "aws_security"],
            "terraform": ["terraform"],
            "kubernetes": ["kubernetes"],
            "finops": ["finops", "aws_finops"],
            "operations": ["aws_operations", "operations"],
            "governance": ["aws_governance", "governance"],
            "aws": ["aws", "cloud_docs"] # fallback main categories
        }
        
    def detect_categories(self, intent: str, query: str) -> List[str]:
        # Start with categories mapped directly from the intent (from PromptBuilder)
        categories = set()
        
        if intent in self.CATEGORY_MAP:
            categories.update(self.CATEGORY_MAP[intent])
            
        # Additional keyword matching for multi-category queries
        query_lower = query.lower()
        if "terraform" in query_lower:
            categories.update(self.CATEGORY_MAP["terraform"])
        if "fail" in query_lower or "blast radius" in query_lower or "outage" in query_lower:
            categories.update(self.CATEGORY_MAP["failure"])
            
        if "production" in query_lower or "best practice" in query_lower or "checklist" in query_lower or "go live" in query_lower:
            categories.update(self.CATEGORY_MAP["production"])
            
        if "terraform" in query_lower or "tf" in query_lower:
            categories.update(self.CATEGORY_MAP["terraform"])
        if "kubernetes" in query_lower or "eks" in query_lower:
            categories.update(self.CATEGORY_MAP["kubernetes"])
        if "security" in query_lower or "guardduty" in query_lower or "iam" in query_lower:
            categories.update(self.CATEGORY_MAP["security"])
        if "cost" in query_lower or "optimize" in query_lower or "billing" in query_lower:
            categories.update(self.CATEGORY_MAP["finops"])
            
        # Ensure 'aws' is included for AWS-specific general queries
        if "aws" in query_lower or "s3" in query_lower or "ec2" in query_lower or "vpc" in query_lower:
            categories.update(self.CATEGORY_MAP["aws"])
            
        # If no categories matched, fallback to general aws
        if not categories:
            categories.update(self.CATEGORY_MAP["aws"])
            
        return list(categories)

    def get_fallback_categories(self, primary_categories: List[str]) -> List[str]:
        """Returns broader categories if primary categories yield few results."""
        fallbacks = set()
        
        if "aws_security" in primary_categories or "security" in primary_categories:
            fallbacks.update(["aws", "architecture"])
            
        if "terraform" in primary_categories:
            fallbacks.update(["aws", "architecture", "kubernetes"])
            
        if "aws_finops" in primary_categories or "finops" in primary_categories:
            fallbacks.update(["aws"])
            
        # Add general AWS docs as ultimate fallback
        fallbacks.update(["aws", "cloud_docs"])
        
        # Remove any that are already in primary
        for cat in primary_categories:
            if cat in fallbacks:
                fallbacks.remove(cat)
                
        return list(fallbacks)