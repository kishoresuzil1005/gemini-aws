class PromptBuilder:
    def __init__(self):
        self.QUESTION_TYPES = {
            "architecture": [
                "architecture", "design", "build", "deploy", "deployment",
                "production", "production-ready", "high availability", "ha",
                "three tier", "3 tier", "microservices", "reference architecture",
                "best architecture", "web application", "web app", "system design",
                "solution architecture", "cloud architecture", "landing zone",
                "multi region", "multi-az", "fault tolerant", "disaster recovery",
                "dr", "scalable", "scalability"
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
            "architecture": """You are a Principal AWS Solutions Architect.

Your responsibilities:
• Design production-grade cloud architectures.
• Follow the AWS Well-Architected Framework.
• Prefer highly available, fault tolerant designs.
• Explain architectural trade-offs.
• Recommend secure and scalable solutions.
• Use AWS best practices.
• Consider networking, IAM, monitoring, backup,
  disaster recovery and cost optimization.

When answering architecture questions always include:
1. Architecture Overview
2. Components
3. Request Flow
4. High Availability
5. Security
6. Scalability
7. Monitoring
8. Disaster Recovery
9. Cost Optimization
10. Best Practices

Only use the retrieved documentation.
Never invent AWS services or configurations.
If information is missing, explicitly say so.""",
            "security": "You are a Senior Cloud Security Engineer.",
            "terraform": "You are a Terraform Infrastructure Expert.",
            "kubernetes": "You are a Kubernetes Platform Engineer.",
            "finops": "You are a Senior FinOps Engineer.",
            "sre": "You are a Senior Site Reliability Engineer.",
            "migration": "You are a Cloud Migration Architect.",
            "default": "You are an Elite Cloud Architect."
        }

        self.SHARED_INSTRUCTIONS = """
You MUST answer ONLY using the retrieved documentation.
Do NOT use prior knowledge.
Do NOT infer.
Do NOT guess.
Do NOT complete missing information.

If the answer is not explicitly present inside the retrieved documentation, reply exactly:
"The retrieved documentation does not contain enough information to answer this question."

Never fabricate AWS services, configurations, commands, or architecture.

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

    def is_architecture_question(self, query: str) -> bool:
        return self.detect_intent(query) == "architecture"

    def build(self, query: str, context: str, architecture_context: dict = None) -> str:
        intent = self.detect_intent(query)
        role_prompt = self.ROLE_PROMPTS.get(intent, self.ROLE_PROMPTS["default"])
        
        architecture_block = ""
        if architecture_context:
            import json
            arch_json = json.dumps(architecture_context, indent=2)
            
            pattern_text = ""
            pattern = architecture_context.get("architecture_pattern")
            if pattern:
                pattern_text = f"""
--- PRODUCTION ARCHITECTURE PATTERN ---
Name: {pattern.get('name', '')}
Description: {pattern.get('description', '')}

Flow:
{' -> '.join(pattern.get('flow', []))}

Recommended Services:
{', '.join(pattern.get('services', []))}

High Availability:
{', '.join(pattern.get('high_availability', []))}

Security:
{', '.join(pattern.get('security', []))}

Monitoring:
{', '.join(pattern.get('monitoring', []))}

Cost Optimization:
{', '.join(pattern.get('cost', []))}

Best Practices:
- {'\n- '.join(pattern.get('best_practices', []))}
---------------------------------------
"""
            architecture_block = f"\n=== ARCHITECTURE CONTEXT ===\n{arch_json}\n{pattern_text}============================\n"

        augmented_prompt = f"""{role_prompt}
{self.SHARED_INSTRUCTIONS}{architecture_block}
=== AWS KNOWLEDGE BASE CONTEXT ===
{context}
==================================

User Question: {query}

Please formulate a precise, highly technical, and actionable response:
"""
        return augmented_prompt
