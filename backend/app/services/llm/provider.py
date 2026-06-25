import os
import logging

logger = logging.getLogger("LLMProvider")


class LLMProvider:

    @staticmethod
    def get_client():
        openai_key = os.getenv("OPENAI_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API")
        
        is_openai_configured = openai_key and len(openai_key) > 10 and "xxxxx" not in openai_key

        try:
            from openai import OpenAI
        except ImportError:
            # Custom resilient adapter if openai module hasn't finished compiling or loading
            class MockChoiceMessage:
                def __init__(self, text):
                    self.content = text

            class MockChoice:
                def __init__(self, text):
                    self.message = MockChoiceMessage(text)

            class MockResponse:
                def __init__(self, text):
                    self.choices = [MockChoice(text)]

            class MockCompletions:
                def create(self, **kwargs):
                    prompt = ""
                    for msg in kwargs.get("messages", []):
                        if msg.get("role") == "user":
                            prompt = msg.get("content", "")
                    
                    if gemini_key:
                        try:
                            import urllib.request
                            import json
                            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
                            payload = {
                                "contents": [{"parts": [{"text": str(prompt)}]}]
                            }
                            req = urllib.request.Request(
                                url,
                                data=json.dumps(payload).encode("utf-8"),
                                headers={"Content-Type": "application/json"},
                                method="POST"
                            )
                            with urllib.request.urlopen(req, timeout=12) as response:
                                res_body = json.loads(response.read().decode("utf-8"))
                                text_out = res_body["candidates"][0]["content"]["parts"][0]["text"]
                                return MockResponse(text_out)
                        except Exception as e:
                            logger.error(f"Fallback direct Gemini API call failed: {e}")
                    
                    return MockResponse(
                        "Stratis LLM fallback channel: Please insert a valid OPENAI_API_KEY "
                        "in your environment values to power the senior FinOps assistant."
                    )

            class MockChat:
                completions = MockCompletions()

            class MockClient:
                chat = MockChat()

            return MockClient()

        if is_openai_configured:
            return OpenAI(api_key=openai_key)
        elif gemini_key:
            return OpenAI(
                api_key=gemini_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
        else:
            return OpenAI(api_key=openai_key or "mock-dummy-key")
