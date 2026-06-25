from app.services.llm.provider import LLMProvider
from app.services.llm.prompt_builder import PromptBuilder


class CloudLLM:

    @staticmethod
    def ask(
        inventory,
        costs,
        recommendations,
        question
    ):

        context = (
            PromptBuilder
            .build_context(
                inventory,
                costs,
                recommendations
            )
        )

        client = (
            LLMProvider
            .get_client()
        )

        base_url = getattr(client, "base_url", None)
        model_name = "gpt-4o-mini"
        if base_url and "googleapis.com" in str(base_url):
            model_name = "gemini-2.5-flash"

        try:
            response = (
                client.chat.completions.create(
                    model=model_name,

                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are Stratis Cloud Copilot, a senior cloud architect, FinOps engineer, "
                                "and DevOps consultant. Analyze the provided cloud inventory resources, monthly billing "
                                "rates, and waste findings to deliver clean, actionable insights."
                            )
                        },
                        {
                            "role": "user",
                            "content": f"{context}\n\nQuestion:\n{question}"
                        }
                    ]
                )
            )

            return (
                response.choices[0]
                .message.content
            )
        except Exception as e:
            # High-fidelity error message fallback
            return (
                f"I parsed your environment with {len(inventory)} resources and "
                f"${costs.get('total', 0.0)} total costs. However, our upstream LLM service is currently "
                f"unreachable or throttled: {str(e)}. Please try checking resource configurations in a moment."
            )
