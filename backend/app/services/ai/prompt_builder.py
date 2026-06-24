class PromptBuilder:

    @staticmethod
    def build(
        resource_id,
        resource_type,
        criticality,
        downstream,
        upstream
    ):

        return f"""
You are a Senior AWS Cloud Architect.

Analyze this resource.

Resource:
{resource_id}

Type:
{resource_type}

Criticality Score:
{criticality}

Downstream Dependencies:
{downstream}

Upstream Dependencies:
{upstream}

Provide:

1. Findings
2. Risks
3. Recommendations
4. Cost Optimizations
5. Security Improvements

Return concise bullet points.
"""
