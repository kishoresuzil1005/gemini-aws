import requests
from app.services.cost.cache import CostSummaryCache

OLLAMA_URL = "http://ollama:11434/api/generate"


class OllamaService:

    @staticmethod
    def generate(prompt: str):

        q = prompt.lower()

        cached = CostSummaryCache.get()

        # Current AWS Cost
        if (
            "current aws cost" in q
            or "current cost" in q
            or "aws spend" in q
        ):

            if cached:
                if hasattr(cached, "actualCost"):
                    act = float(cached.actualCost)
                    fore = float(cached.forecastCost)
                else:
                    act = float(cached.get("actualCost", 0.0))
                    fore = float(cached.get("forecastCost", 0.0))

                return (
                    f"Current AWS spend is "
                    f"${act:.2f}. "
                    f"Forecast month-end spend is "
                    f"${fore:.2f}."
                )

        # Highest Cost Service
        if (
            "which service costs the most" in q
            or "highest cost service" in q
            or "most expensive service" in q
        ):

            if cached:
                services = getattr(cached, "byService", None) or cached.get("byService", [])
                if services:
                    top_service = "Unknown"
                    top_amount = 0.0
                    for svc in services:
                        if hasattr(svc, "amount"):
                            name = svc.service
                            amt = float(svc.amount)
                        else:
                            name = svc.get("service", "Unknown")
                            amt = float(svc.get("amount", svc.get("cost", 0.0)))
                        if amt > top_amount:
                            top_service = name
                            top_amount = amt

                    if hasattr(cached, "actualCost"):
                        act = float(cached.actualCost)
                        fore = float(cached.forecastCost)
                    else:
                        act = float(cached.get("actualCost", 0.0))
                        fore = float(cached.get("forecastCost", 0.0))

                    return (
                        f"{top_service} is currently "
                        f"the highest cost service at "
                        f"${top_amount:.2f}. "
                        f"Current AWS spend is "
                        f"${act:.2f}. "
                        f"Forecast spend is "
                        f"${fore:.2f}."
                    )

        # Fallback to Ollama
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "qwen2.5:1.5b",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 256,
                    "temperature": 0.2
                }
            },
            timeout=120
        )

        response.raise_for_status()

        return response.json()["response"]
