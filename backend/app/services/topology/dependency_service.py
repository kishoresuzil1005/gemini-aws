from app.models import ResourceNodeDB, ResourceEdgeDB

class DependencyService:
    def __init__(self, db):
        self.db = db

    def get_resource_dependencies(self, resource_id: str):
        node = self.db.query(ResourceNodeDB).filter(ResourceNodeDB.resource_id == resource_id).first()
        if not node:
            return None
            
        edges = self.db.query(ResourceEdgeDB).filter(ResourceEdgeDB.source_id == resource_id).all()
        dependencies = []
        for e in edges:
            target = self.db.query(ResourceNodeDB).filter(ResourceNodeDB.resource_id == e.target_id).first()
            if target:
                dependencies.append({
                    "type": target.resource_type,
                    "name": target.name or target.resource_id
                })
                
        return {
            "resource": {
                "id": node.resource_id,
                "name": node.name or node.resource_id
            },
            "dependencies": dependencies
        }

    def get_resource_graph(self, resource_id: str):
        node = self.db.query(ResourceNodeDB).filter(ResourceNodeDB.resource_id == resource_id).first()
        if not node:
            return None

        # 1. Direct dependencies: outbound connections
        outbound_edges = self.db.query(ResourceEdgeDB).filter(ResourceEdgeDB.source_id == resource_id).all()
        # 2. Incoming dependencies: inbound connections (who depends on me)
        inbound_edges = self.db.query(ResourceEdgeDB).filter(ResourceEdgeDB.target_id == resource_id).all()

        nodes_map = {}
        # Core node
        nodes_map[resource_id] = {
            "id": node.resource_id,
            "type": node.resource_type,
            "name": node.name or node.resource_id
        }

        # Sub-nodes
        for e in outbound_edges + inbound_edges:
            for rid in (e.source_id, e.target_id):
                if rid not in nodes_map:
                    rn = self.db.query(ResourceNodeDB).filter(ResourceNodeDB.resource_id == rid).first()
                    if rn:
                        nodes_map[rid] = {
                            "id": rn.resource_id,
                            "type": rn.resource_type,
                            "name": rn.name or rn.resource_id
                        }
                    else:
                        # Fallback placeholder node
                        nodes_map[rid] = {
                            "id": rid,
                            "type": "VPC" if rid.startswith("vpc-") else ("SUBNET" if rid.startswith("subnet-") else "Resource"),
                            "name": rid
                        }

        # Build list of nodes (excluding query node if preferred, but usually returning all for full view)
        nodes_list = list(nodes_map.values())

        # Build list of edges
        edges_list = []
        seen_edges = set()
        for e in outbound_edges:
            edge_key = (e.source_id, e.target_id, e.relationship)
            if edge_key not in seen_edges:
                edges_list.append({
                    "source": e.source_id,
                    "target": e.target_id,
                    "relation": (e.relationship or "depends_on").upper()
                })
                seen_edges.add(edge_key)
        for e in inbound_edges:
            edge_key = (e.source_id, e.target_id, e.relationship)
            if edge_key not in seen_edges:
                edges_list.append({
                    "source": e.source_id,
                    "target": e.target_id,
                    "relation": (e.relationship or "depends_on").upper()
                })
                seen_edges.add(edge_key)

        # 3. Dynamic Impact Analysis Tracing
        impact_analysis = []

        # Inbound dependencies are directly impacted by me (if me is removed, they break)
        for e in inbound_edges:
            dep_node = self.db.query(ResourceNodeDB).filter(ResourceNodeDB.resource_id == e.source_id).first()
            if dep_node:
                impact_text = f"Direct dependency on {node.resource_id}. "
                if dep_node.resource_type == "EC2":
                    impact_text += "EC2 server hosting services will lose connection or fail runtime calls."
                elif dep_node.resource_type == "RDS":
                    impact_text += "RDS database subnet/routing or security rules will be disconnected."
                elif dep_node.resource_type == "ALB":
                    impact_text += "ALB targets will become healthy/unhealthy with broken routing."
                else:
                    impact_text += f"{dep_node.resource_type} service components will trigger health check failures."
                    
                impact_analysis.append({
                    "id": dep_node.resource_id,
                    "type": dep_node.resource_type,
                    "name": dep_node.name or dep_node.resource_id,
                    "impact": impact_text
                })

        # Outbound dependencies impacted (effects of removing me)
        for e in outbound_edges:
            comp_node = self.db.query(ResourceNodeDB).filter(ResourceNodeDB.resource_id == e.target_id).first()
            if comp_node:
                impact_text = ""
                if node.resource_type == "EC2" and comp_node.resource_type == "EBS":
                    impact_text = f"Volume unattached. Dynamic storage block leaks or data loss on {comp_node.resource_id}."
                elif node.resource_type == "EC2" and comp_node.resource_type == "SecurityGroup":
                    impact_text = f"Decoupled security group. {comp_node.resource_id} loses its ingress traffic binding."
                elif node.resource_type == "EC2" and comp_node.resource_type == "Subnet":
                    impact_text = "Frees underlying IP networking allocation on corporate subnet."
                elif node.resource_type == "RDS" and comp_node.resource_type == "VPC":
                    impact_text = f"RDS DB deallocated from database subnet group on VPC network {comp_node.resource_id}."
                else:
                    impact_text = f"Closes network or operational connection to component {comp_node.resource_id}."
                
                if impact_text:
                    impact_analysis.append({
                        "id": comp_node.resource_id,
                        "type": comp_node.resource_type,
                        "name": comp_node.name or comp_node.resource_id,
                        "impact": impact_text
                    })

        # Add generalized self-deconstruction impact estimate based on node type
        self_impact = ""
        r_type = node.resource_type.upper()
        if r_type == "VPC":
            self_impact = "CRITICAL RISK: Deleting this VPC terminates all subnets, active routing tables, firewalls, and hosted instances inside its network scope."
        elif r_type in ("SUBNET", "SUBNETS"):
            self_impact = "HIGH RISK: Deleting this Subnet disrupts/disconnects all nested server interfaces, private IPs, and target group bindings."
        elif r_type in ("SECURITYGROUP", "SECURITY_GROUP", "SECURITY_GROUPS"):
            self_impact = "SERVICE RISK: Deleting this Security Group leaves associated database endpoints and EC2 servers without ingress/egress firewalls."
        elif r_type == "EBS":
            self_impact = "DATA LOSS RISK: Removing this EBS disk hard block permanently drops database tables, block files, and local logs."
        elif r_type == "EC2":
            self_impact = "SERVICE OUTAGE: Restarts or halts virtual machine instance workloads, shutting down target microservice container points."
        elif r_type == "RDS":
            self_impact = "CRITICAL OUTAGE: Dropping database clusters stops backend SQL connections, triggering immediate frontend failures."
            
        if self_impact:
            impact_analysis.append({
                "id": node.resource_id,
                "type": node.resource_type,
                "name": node.name or node.resource_id,
                "impact": self_impact
            })

        return {
            "resource": {
                "id": node.resource_id,
                "type": node.resource_type,
                "name": node.name or node.resource_id
            },
            "nodes": nodes_list,
            "edges": edges_list,
            "impact_analysis": impact_analysis
        }
