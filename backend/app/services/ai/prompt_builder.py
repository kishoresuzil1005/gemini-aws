class PromptBuilder:
    def __init__(self):
        self.QUESTION_TYPES = {
            "architecture": [
                "architecture", "design", "ha", "high availability",
                "three tier", "vpc", "alb", "load balancer"
            ],
            "security": [
                "security", "iam", "kms", "guardduty", "cloudtrail",
                "inspector", "mfa", "encryption"
            ],
            "terraform": [
                "terraform", "provider", "module", "backend", "state", "tf"
            ],
            "kubernetes": [
                "kubernetes", "eks", "pod", "deployment", "service",
                "statefulset", "daemonset", "ingress"
            ],
            "finops": [
                "cost", "billing", "budget", "pricing", "savings",
                "reserved", "spot", "rightsizing"
            ],
            "sre": [
                "cpu", "memory", "disk", "network", "latency", "logs",
                "error", "crash", "monitoring", "cloudwatch"
            ],
            "migration": [
                "migration", "migrate", "azure", "gcp", "on-prem"
            ]
        }

        self.ROLE_PROMPTS = {
            "architecture": "You are a Senior AWS Solutions Architect.",
            "security": "You are a Senior Cloud Security Engineer.",
            "terraform": "You are a Terraform Infrastructure Expert.",
            "kubernetes": "You are a Kubernetes Platform Engineer.",
            "finops": "You are a Senior FinOps Engineer.",
            "sre": "You are a Senior Site Reliability Engineer.",
            "migration": "You are a Cloud Migration Architect.",
            "default": "You are an Elite Cloud Architect."
        }

        self.SHARED_INSTRUCTIONS = """
Always:
• Use ONLY the retrieved documentation.
• Never invent information.
• If documentation is missing, say:
"The retrieved documentation does not contain enough information."

Always provide:
1. Explanation
2. Best Practices
3. Production Recommendations
4. AWS Services Used
5. Security Considerations
6. Cost Optimization
7. Common Mistakes
8. References to retrieved documentation.
"""

    def detect_intent(self, query: str) -> str:
        query_lower = query.lower()
        for intent, keywords in self.QUESTION_TYPES.items():
            if any(keyword in query_lower for keyword in keywords):
                return intent
        return "default"

    def build(self, query: str, context: str) -> str:
        intent = self.detect_intent(query)
        role_prompt = self.ROLE_PROMPTS.get(intent, self.ROLE_PROMPTS["default"])

        augmented_prompt = f"""{role_prompt}
{self.SHARED_INSTRUCTIONS}

=== AWS KNOWLEDGE BASE CONTEXT ===
{context}
==================================

User Question: {query}

Please formulate a precise, highly technical, and actionable response:
"""
        return augmented_prompt
