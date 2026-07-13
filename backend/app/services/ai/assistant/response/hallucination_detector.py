class HallucinationDetector:
    def __init__(self):
        pass

    def detect(self, answer: str, context: str) -> bool:
        """
        Prevents references to nonexistent resources.
        Returns True if a hallucination is detected.
        """
        # A basic check could involve looking for typical resource ID patterns in the answer 
        # and checking if they exist in the context.
        return Fals