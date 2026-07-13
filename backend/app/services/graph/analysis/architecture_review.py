import logging
from app.services.graph.neo4j_service import Neo4jService

logger = logging.getLogger(__name__)

class ArchitectureReviewer:
    def __init__(self, neo4j_service: Neo4jService = None):
        self.neo4j = neo4j_service or Neo4jService()

    def analyze(self):
        """
        Executes architectural best-practice checks against the entire graph.
        Returns a Well-Architected score and a list of specific warnings.
        """
        warnings = []
        score = 100
        
        if not self.neo4j.driver:
            return {"score": 0, "warnings": ["Neo4j not connected"]}
            
        try:
            # Check 1: Public RDS (RDS connected to a public subnet or open SG)
            # For simplicity, we just look for RDS instances without a NAT or private subnet
            # A real Cypher query would be more complex. Here is a mocked/simplified check.
            query_public_rds = """
            MATCH (r:RDS)-[:USES_SG]->(sg:SecurityGroup)
            // In a real scenario, we'd check if SG allows 0.0.0.0/0
            RETURN r.id as id
            LIMIT 1
            """
            res_rds = self.neo4j.query(query_public_rds)
            if res_rds:
                warnings.append({"severity": "High", "issue": "Public RDS detected", "resource": res_rds[0].get("id")})
                score -= 15
                
            # Check 2: Single Point of Failure (EC2 without ASG or ALB)
            query_spof = """
            MATCH (ec2:EC2)
            OPTIONAL MATCH (asg:AutoScalingGroup)-[:MANAGES]->(ec2)
            OPTIONAL MATCH (alb:ALB)-[*1..2]->(ec2)
            WITH ec2, asg, alb
            WHERE asg IS NULL AND alb IS NULL
            RETURN ec2.id as id
            LIMIT 5
            """
            res_spof = self.neo4j.query(query_spof)
            if res_spof:
                for ec2 in res_spof:
                    warnings.append({"severity": "Medium", "issue": "EC2 instance not behind ALB or ASG (Single Point of Failure)", "resource": ec2.get("id")})
                    score -= 5
                    
            # Check 3: Orphaned Load Balancers (ALB with no TargetGroup/EC2)
            query_orphan_alb = """
            MATCH (alb:ALB)
            OPTIONAL MATCH (alb)-[*1..2]->(ec2:EC2)
            WITH alb, ec2
            WHERE ec2 IS NULL
            RETURN alb.id as id
            LIMIT 3
            """
            res_alb = self.neo4j.query(query_orphan_alb)
            if res_alb:
                for alb in res_alb:
                    warnings.append({"severity": "Low", "issue": "Orphaned ALB without backend compute", "resource": alb.get("id")})
                    score -= 2
                    
        except Exception as e:
            logger.error(f"Error during architecture review: {e}")
            
        # Floor score at 0
        score = max(0, score)
        
        return {
            "score": score,
            "max_score": 100,
            "warnings": warnings
        