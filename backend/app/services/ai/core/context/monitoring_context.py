from typing import Dict


class MonitoringContext:
    """
    Placeholder for CloudWatch / monitoring metrics context.

    In a later phase this will pull real-time CPU, memory,
    disk, latency, and error-rate data from CloudWatch or
    a Prometheus-compatible endpoint.
    """

    def __init__(self):
        pass

    def build(self, intent) -> Dict:
        """
        Returns monitoring context for the given intent.

        Currently returns an empty placeholder so the rest
        of the pipeline can operate without CloudWatch access.
        """

        return {
            "available": False,
            "message": "Monitoring integration coming in Phase AI-2.",
            "metrics": []
        }
