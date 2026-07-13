class ExplanationBuilder:
    def __init__(self):
        pass

    def build_explanation(self, llm_answer: str, evidence: list, sources: list) -> str:
        """
        Turns technical findings into clear operational explanations.
        """
        # In a real implementation this might use another LLM call or template
        # to format the final explanation.
        return f"{llm_answer}