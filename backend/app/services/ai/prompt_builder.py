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
            review_text = ""
            review_context = architecture_context.get("review_context")
            if review_context:
                inventory_str = "\n".join([f"{k}: {v}" for k, v in review_context.get("inventory", {}).items()])
                findings_str = "\n".join(
                    review_context.get("spofs", []) +
                    review_context.get("security_findings", []) +
                    review_context.get("cost_findings", []) +
                    review_context.get("reliability_findings", []) +
                    review_context.get("network_findings", []) +
                    review_context.get("monitoring_findings", [])
                )
                
                review_text = f"""
--- ARCHITECTURE REVIEW FINDINGS ---
Current Environment Inventory:
{inventory_str}

Graph Context:
Nodes Analyzed: {review_context.get('graph', {}).get('nodes_analyzed', 0)}
Relationships Found: {review_context.get('graph', {}).get('relationships_found', 0)}
Orphan Resources: {review_context.get('graph', {}).get('orphan_resources', 0)}

Criticality Context:
High Risk Assets: {review_context.get('criticality', {}).get('high_risk_assets', 0)}
Average Blast Radius: {review_context.get('criticality', {}).get('average_blast_radius', 0.0)}

Detected Findings & Risks:
{findings_str if findings_str else 'No findings detected.'}

"""
                score_data = review_context.get("scoring")
                if score_data:
                    pillars = score_data.get('pillar_scores', {})
                    review_text += f"""
Architecture Score
Overall: {score_data.get('overall_score', 0)}/100 (Grade {score_data.get('grade', 'N/A')})

Pillar Breakdown:
Availability: {pillars.get('availability', 0)}/10
Security: {pillars.get('security', 0)}/10
Reliability: {pillars.get('reliability', 0)}/10
Performance: {pillars.get('performance', 0)}/10
Cost: {pillars.get('cost', 0)}/10
Operational Excellence: {pillars.get('operational_excellence', 0)}/10
Sustainability: {pillars.get('sustainability', 0)}/10
"""
                
                wa_data = review_context.get("well_architected")
                if wa_data:
                    review_text += "\n--- AWS WELL-ARCHITECTED REVIEW ---\n"
                    for pillar_name, p_data in wa_data.items():
                        title = pillar_name.replace("_", " ").title()
                        str_list = '\n  - '.join(p_data.get('strengths', [])) if p_data.get('strengths') else "None detected."
                        weak_list = '\n  - '.join(p_data.get('weaknesses', [])) if p_data.get('weaknesses') else "None detected."
                        rec_list = '\n  - '.join(p_data.get('recommendations', [])) if p_data.get('recommendations') else "None."
                        
                        review_text += f"""
{title} (Score: {p_data.get('score', 0)}/10)
Strengths:
  - {str_list}
Weaknesses:
  - {weak_list}
Recommendations:
  - {rec_list}
"""
                
                recs_data = review_context.get("recommendations", [])
                if recs_data:
                    review_text += "\n--- ARCHITECTURE RECOMMENDATIONS ---\n"
                    for rec in recs_data:
                        review_text += f"""
[{rec.get('priority', 'UNKNOWN')}] {rec.get('title', 'Unknown')} (Category: {rec.get('category', 'General')})
Reason: {rec.get('reason', '')}
Business Impact: {rec.get('business_impact', '')}
Current State: {rec.get('current_state', '')}
Recommended State: {rec.get('recommended_state', '')}
Implementation Steps:
  - {'\n  - '.join(rec.get('implementation_steps', []))}
AWS Services: {', '.join(rec.get('aws_services', []))}
"""
                review_text += "------------------------------------\n"
                
            failure_context = architecture_context.get("failure_context")
            if failure_context:
                review_text += f"""
--- FAILURE ANALYSIS REPORT ---
Failed Resource: {failure_context.get('resource', 'Unknown')}
Severity: {failure_context.get('severity', 'UNKNOWN')}
Criticality Score: {failure_context.get('criticality_score', 0)}/10
Blast Radius (Affected Nodes): {failure_context.get('blast_radius', 0)}
Estimated Recovery Time: {failure_context.get('estimated_recovery', 'Unknown')}

Business Impact:
  - {'\n  - '.join(failure_context.get('business_impact', []))}

Affected Services (Downstream):
  - {', '.join(failure_context.get('affected_services', []))}

Likely Root Causes:
  - {', '.join(failure_context.get('likely_root_causes', []))}

Recovery Plan & Recommendations:
  - {'\n  - '.join(failure_context.get('recommendations', []))}
-------------------------------
"""

            architecture_block = f"\n=== ARCHITECTURE CONTEXT ===\n{arch_json}\n{pattern_text}{review_text}============================\n"

        augmented_prompt = f"""{role_prompt}
{self.SHARED_INSTRUCTIONS}{architecture_block}
=== AWS KNOWLEDGE BASE CONTEXT ===
{context}
==================================

User Question: {query}

Please formulate a precise, highly technical, and actionable response:
"""
        return augmented_prompt
