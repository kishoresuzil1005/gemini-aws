from app.services.graph.graph_analysis_service import GraphAnalysisService
from app.services.graph.neo4j_service import Neo4jService

class CriticalityService:

    def __init__(self):
        self.analysis = GraphAnalysisService()
        self.neo4j = Neo4jService()

    def calculate(self, resource_id):
        upstream_list = self.analysis.upstream_dependencies(resource_id)
        upstream = len(upstream_list) if upstream_list else 0

        downstream_list = self.analysis.downstream_dependencies(resource_id)
        downstream = len(downstream_list) if downstream_list else 0

        blast_data = self.analysis.blast_radius(resource_id)
        blast = blast_data.get("impacted", 0) if blast_data else 0

        score = upstream + downstream + blast

        if score >= 15:
            level = "CRITICAL"
        elif score >= 8:
            level = "HIGH"
        elif score >= 4:
            level = "MEDIUM"
        else:
            level = "LOW"

        return {
            "resource": resource_id,
            "upstream": upstream,
            "downstream": downstream,
            "blast_radius": blast,
            "score": score,
            "criticality": level
        }

    def top_critical(self):
        if not self.neo4j.driver:
            return []
        
        try:
            query = """
            MATCH (n)
            RETURN n.id AS id, labels(n)[0] AS type
            """
            nodes = self.neo4j.query(query)
            if not nodes:
                return []
            
            results = []
            for node in nodes:
                node_id = node.get("id")
                if not node_id:
                    continue
                calc = self.calculate(node_id)
                results.append({
                    "resource": node_id,
                    "type": node.get("type", "Unknown"),
                    "score": calc["score"]
                })
            
            # Sort by score DESC
            results.sort(key=lambda x: x["score"], reverse=True)
            
            # Return top 20
            return results[:20]
        except Exception as e:
            return []
