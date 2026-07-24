import logging
from knowledge.service.client_factory import get_default_client

logger = logging.getLogger(__name__)

class NLQueryEngine:
    def __init__(self, knowledge_client=None):
        self.client = knowledge_client or get_default_client()

    def execute_query(self, natural_language_query: str):
        """
        Translates a natural language question into a query,
        executes it against the Knowledge Service, and returns the result.
        """
        # MOCK LLM TRANSLATION
        cypher_query = ""
        mock_result = []
        
        lower_q = natural_language_query.lower()
        
        if "lambda" in lower_q and "iam" in lower_q:
            cypher_query = "MATCH (l:Lambda)-[:USES_ROLE]->(r:IAM_ROLE) RETURN l.id, r.id"
            mock_result = [{"l.id": "my-lambda-func", "r.id": "arn:aws:iam::123:role/LambdaRole"}]
        elif "database" in lower_q and "application" in lower_q:
            cypher_query = "MATCH (app)-[*1..3]->(db:RDS) RETURN app.id, db.id"
            mock_result = [{"app.id": "api-gateway-123", "db.id": "rds-main-db"}]
        else:
            cypher_query = "MATCH (n) RETURN n LIMIT 5"
            mock_result = [{"n": "MOCK_NODE_DATA"}]
            
        # Execute query via Knowledge Service
        db_results = []
        try:
            db_results = self.client.query_graph(cypher_query)
        except NotImplementedError:
            logger.warning("Graph querying not fully implemented in Knowledge Service.")
            db_results = mock_result
        except Exception as e:
            logger.error(f"Error executing AI generated query: {e}")
            db_results = [{"error": str(e)}]
            
        return {
            "query_provided": natural_language_query,
            "cypher_generated": cypher_query,
            "results": db_results
        }