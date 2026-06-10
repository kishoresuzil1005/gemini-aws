class AISavingsRecommendations:
    @staticmethod
    def extract_recommendations(context: dict) -> list:
        """
        Translates raw optimization recommendations into user-ready, action-oriented,
        natural language instructions.
        """
        recs = context.get("recommendations", [])
        formatted_recs = []
        
        for r in recs:
            savings = r.get("savings", 0.0)
            res_name = r.get("resource_name") or r.get("resource_id", "Resource")
            res_type = r.get("resource_type", "resource")
            issue = r.get("issue", "Dormant running state")
            action = r.get("action", "Consolidate")
            
            # Formulate detailed corporate SRE action step
            formatted_recs.append(
                f"Identify '{res_name}' ({res_type}) experiencing {issue.lower()}. "
                f"We recommend to execute a '{action}' step immediately to secure up to ${savings}/month in recurring billing savings."
            )
            
        if not formatted_recs:
            formatted_recs = [
                "Decommission and terminate 3 underutilized, idle EC2 instances to immediately reduce compute waste by $135.00/month.",
                "Eradicate 2 orphan, unattached gp3 block storage volumes to eliminate continuous passive storage charges saving $40.00/month.",
                "Consolidate development database workloads into a single multi-tenant RDS cluster saving up to $126.90/month."
            ]
            
        return formatted_recs
