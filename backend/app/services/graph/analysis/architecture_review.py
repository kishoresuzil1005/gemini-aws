import logging
from knowledge.service.client_factory import get_default_client

logger = logging.getLogger(__name__)

class ArchitectureReviewer:
    def __init__(self, knowledge_client=None):
        self.client = knowledge_client or get_default_client()

    def analyze(self):
        """
        Executes architectural best-practice checks against the entire knowledge graph.
        Returns a Well-Architected score and a list of specific warnings.
        """
        warnings = []
        score = 100
        
        try:
            # Fetch architecture rules from the Knowledge Service
            arch_rules = self.client.get_rules(category="architecture")
            
            # For each rule, evaluate against the graph
            # If a rule has a query, we could execute it via client.query_graph
            for rule in arch_rules:
                rule_name = rule.get("name", "Unknown Rule")
                severity = rule.get("severity", "Medium")
                penalty = rule.get("score_penalty", 5)
                query = rule.get("query")
                
                if query:
                    try:
                        violating_resources = self.client.query_graph(query)
                        if violating_resources:
                            for res in violating_resources:
                                warnings.append({
                                    "severity": severity,
                                    "issue": f"{rule_name} violation",
                                    "resource": res.get("id", "unknown")
                                })
                                score -= penalty
                    except NotImplementedError:
                        logger.warning("Graph querying not fully implemented in Knowledge Service.")
                        pass
                    except Exception as e:
                        logger.error(f"Error evaluating rule {rule_name}: {e}")
                        
        except Exception as e:
            logger.error(f"Error during architecture review: {e}")
            
        # Floor score at 0
        score = max(0, score)
        
        return {
            "score": score,
            "max_score": 100,
            "warnings": warnings
        }