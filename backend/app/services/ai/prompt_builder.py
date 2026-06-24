class PromptBuilder:

    @staticmethod
    def build(
        resource_id,
        resource_type,
        criticality,
        blast_radius,
        graph_context
    ):

        context = ""

        for row in graph_context:

            context += (
                f"{row['relationship']} -> "
                f"{row['target']} "
                f"({row['target_type']})\n"
            )

        return f"""
You are a Senior AWS Cloud Architect.

Analyze the following AWS resource.

Resource:
{resource_id}

Type:
{resource_type}

Criticality Score:
{criticality}

Blast Radius:
{blast_radius}

Dependencies:
{context}

Provide:

1. Findings
2. Risks
3. Recommendations
4. Cost Optimization
5. Security Improvements

Keep answer concise.
"""
