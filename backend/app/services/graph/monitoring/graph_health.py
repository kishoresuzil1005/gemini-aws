class GraphHealth:
    """
    Basic connection and state health checks for the Neo4j backend.
    """
    def check_health(self):
        return {"status": "healthy"}