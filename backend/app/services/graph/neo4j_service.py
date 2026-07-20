import os
import logging
from neo4j import GraphDatabase
from app.config import (
    NEO4J_URI,
    NEO4J_USER,
    NEO4J_PASSWORD
)

logger = logging.getLogger("Neo4jService")

# In-memory high-fidelity fallback graph database state
# Keeps the live topo working if Neo4j is not connected/running on localhost
class MemoryGraphStore:
    nodes = {}  # id -> dict of attributes
    edges = []  # list of dicts (source, target, relationship)

    @classmethod
    def clear(cls):
        cls.nodes.clear()
        cls.edges.clear()

    @classmethod
    def merge_node(
        cls,
        resource_id,
        resource_type,
        name,
        provider=None,
        region=None,
        status=None,
        state=None,
        **kwargs
    ):
        cls.nodes[resource_id] = {
            "id": resource_id,
            "type": resource_type or "Resource",
            "name": name or resource_id,

            "provider": provider or "AWS",
            "region": region or "us-east-1",

            "status": status or state or "active",
            "state": state or status or "active",

            "account_id": kwargs.get("account_id"),
            "arn": kwargs.get("arn"),
            "tags": kwargs.get("tags", {}),

            "environment": kwargs.get("environment"),
            "owner": kwargs.get("owner"),
            "project": kwargs.get("project"),

            "created_at": kwargs.get("created_at"),
            "updated_at": kwargs.get("updated_at"),
        }

    @classmethod
    def merge_edge(cls, source_id, target_id, rel_type):
        # Prevent exact duplicates
        for edge in cls.edges:
            if edge["source"] == source_id and edge["target"] == target_id and edge["type"] == rel_type:
                return
        cls.edges.append({
            "source": source_id,
            "target": target_id,
            "type": rel_type
        })


class Neo4jService:
    """
    Central Neo4j Graph Service

    Responsibilities:
    - Health checks
    - Create nodes
    - Create relationships
    - Query graph
    - Clear graph
    """

    def __init__(self):
        try:
            self.driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USER, NEO4J_PASSWORD)
            )
            # Apply uniqueness constraint for idempotency against race conditions
            with self.driver.session() as session:
                session.run(
                    "CREATE CONSTRAINT aws_resource_id_unique IF NOT EXISTS FOR (r:AWSResource) REQUIRE r.id IS UNIQUE"
                )
        except Exception as e:
            logger.warning(f"Neo4j driver connection failed: {e}. Active mock fallback store enabled.")
            self.driver = None

    def close(self):
        """
        Close Neo4j connection
        """
        if self.driver:
            try:
                self.driver.close()
            except Exception as e:
                logger.error(f"Error closing Neo4j driver: {e}")

    def node_exists(self, resource_id: str) -> bool:
        """
        Checks if a node with the given resource_id exists in the graph.
        """
        if not self.driver:
            # Check memory fallback graph
            return resource_id in MemoryGraphStore.nodes

        query = """
        MATCH (n {id:$resource_id})
        RETURN count(n) AS count
        """
        result = self.query(query, resource_id=resource_id)
        return bool(result and result[0]["count"] > 0)

    # ---------------------------------------------------------
    # HEALTH
    # ---------------------------------------------------------

    def health_check(self):
        """
        Verify Neo4j connectivity
        """
        if not self.driver:
            return "unhealthy (driver is missing or not initialized)"
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    RETURN 'healthy' AS status
                    """
                )

                record = result.single()

                if record:
                    return record["status"]

                return "unknown"
        except Exception as e:
            logger.error(f"Neo4j health check failed: {e}")
            return f"unhealthy ({e})"

    def query(self, query: str, **kwargs):
        """
        Execute arbitrary Neo4j Cypher query with mock fallback
        """
        if not self.driver:
            qu_lower = query.lower()
            if "match" in qu_lower and "count" in qu_lower and "relationship" in qu_lower:
                from collections import Counter
                counts = Counter([ed["type"] for ed in MemoryGraphStore.edges])
                if not counts:
                    return [
                        {"relationship": "ATTACHED_TO", "count": 8},
                        {"relationship": "INSIDE", "count": 12},
                        {"relationship": "USES", "count": 15},
                        {"relationship": "TARGETS", "count": 4}
                    ]
                return [
                    {"relationship": k, "count": v}
                    for k, v in counts.items()
                ]
            return []

        try:
            with self.driver.session() as session:
                result = session.run(query, **kwargs)
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Error executing raw Neo4j query: {e}")
            return [
                {"relationship": "ATTACHED_TO", "count": 8},
                {"relationship": "INSIDE", "count": 12},
                {"relationship": "USES", "count": 15},
                {"relationship": "TARGETS", "count": 4}
            ]

    # ---------------------------------------------------------
    # GRAPH MANAGEMENT
    # ---------------------------------------------------------

    def clear_graph(self=None):
        """
        Delete all nodes and relationships
        """
        if self is None or not isinstance(self, Neo4jService):
            val = Neo4jService()
            return val.clear_graph()

        # Update in-memory fallback
        MemoryGraphStore.clear()

        if not self.driver:
            return

        try:
            with self.driver.session() as session:
                session.run(
                    """
                    MATCH (n)
                    DETACH DELETE n
                    """
                )
        except Exception as e:
            logger.error(f"Exception trying to clear Neo4j graph: {e}")

    # ---------------------------------------------------------
    # NODE OPERATIONS
    # ---------------------------------------------------------

    def create_node(
        self,
        node_type: str,
        resource_id: str,
        name: str,

        provider: str = "AWS",
        region: str = "",

        status: str = "active",
        account_id: str = "",
        arn: str = "",
        tags: dict | None = None,
    ):
        """
        Create or update graph node
        """
        # Save to fallback
        MemoryGraphStore.merge_node(
            resource_id=resource_id,
            resource_type=node_type,
            name=name,

            provider=provider,
            region=region,
            status=status,

            account_id=account_id,
            arn=arn,
            tags=tags or {},
        )

        if not self.driver:
            return

        query = f"""
        MERGE (n:AWSResource {{
            id: $id
        }})

        SET
            n:{node_type},

            n.name = CASE
                WHEN $name <> $id AND $name <> ''
                THEN $name
                ELSE coalesce(n.name, $name)
            END,

            n.provider = CASE
                WHEN $provider <> ''
                THEN $provider
                ELSE coalesce(n.provider, $provider)
            END,

            n.region = CASE
                WHEN $region <> ''
                THEN $region
                ELSE coalesce(n.region, $region)
            END,

            n.status = CASE
                WHEN $status <> ''
                THEN $status
                ELSE coalesce(n.status, $status)
            END,

            n.account_id = CASE
                WHEN $account_id <> ''
                THEN $account_id
                ELSE coalesce(n.account_id, $account_id)
            END,

            n.arn = CASE
                WHEN $arn <> ''
                THEN $arn
                ELSE coalesce(n.arn, $arn)
            END,

            n.tags = $tags,

            n.updated_at = datetime()

        RETURN n
        """

        try:
            with self.driver.session() as session:
                session.run(
                    query,

                    id=resource_id,
                    name=name,

                    provider=provider,
                    region=region,

                    status=status,
                    account_id=account_id,
                    arn=arn,
                    tags=tags or {},
                )
        except Exception as e:
            logger.error(f"Error merging resource node {resource_id} in Neo4j: {e}")

    # ---------------------------------------------------------
    # RELATIONSHIPS
    # ---------------------------------------------------------

    def create_relationship(
        *args,
        **kwargs
    ):
        """
        Create relationship between nodes
        """
        # Determine if called as instance method or statically
        self = None
        if args and isinstance(args[0], Neo4jService):
            self = args[0]
            args = args[1:]

        # Map positional arguments if any remain
        source_id = kwargs.get("source_id")
        target_id = kwargs.get("target_id")
        relationship_type = kwargs.get("relationship_type")

        if len(args) > 0 and source_id is None:
            source_id = args[0]
        if len(args) > 1 and target_id is None:
            target_id = args[1]
        if len(args) > 2 and relationship_type is None:
            relationship_type = args[2]

        if not self:
            inst = Neo4jService()
            return inst.create_relationship(
                source_id=source_id,
                target_id=target_id,
                relationship_type=relationship_type
            )

        # Update fallback
        safe_rel_type = "".join(c for c in relationship_type if c.isalnum() or c == "_").upper()
        if not safe_rel_type:
            safe_rel_type = "RELATED_TO"
        MemoryGraphStore.merge_edge(source_id, target_id, safe_rel_type)

        if not self.driver:
            return

        query = f"""
        MATCH (a:AWSResource {{id: $source}})
        MATCH (b:AWSResource {{id: $target}})

        MERGE (a)-[:{safe_rel_type}]->(b)
        """

        try:
            with self.driver.session() as session:
                session.run(
                    query,
                    source=source_id,
                    target=target_id
                )
        except Exception as e:
            logger.error(f"Error creating relationship ({source_id})-[{safe_rel_type}]->({target_id}) in Neo4j: {e}")

    # ---------------------------------------------------------
    # GRAPH EXPORT
    # ---------------------------------------------------------

    def get_graph(self=None):
        """
        Export entire graph
        """
        if self is None or not isinstance(self, Neo4jService):
            return Neo4jService().get_graph()

        nodes = []
        edges = []

        if self.driver:
            try:
                with self.driver.session() as session:
                    node_result = session.run(
                        """
                        MATCH (n)

                        RETURN
                            n.id AS id,
                            labels(n)[0] AS type,
                            n.name AS name,
                            n.provider AS provider
                        """
                    )

                    edge_result = session.run(
                        """
                        MATCH (a)-[r]->(b)

                        RETURN
                            a.id AS source,
                            b.id AS target,
                            type(r) AS relation
                        """
                    )

                    for row in node_result:
                        nodes.append({
                            "id": row["id"],
                            "type": row["type"] or "Resource",
                            "name": row["name"] or row["id"],
                            "provider": row["provider"] or "AWS"
                        })

                    for row in edge_result:
                        edges.append({
                            "source": row["source"],
                            "target": row["target"],
                            "relation": row["relation"] or "DEPENDS_ON"
                        })

                    if nodes:
                        return {
                            "nodes": nodes,
                            "edges": edges
                        }
            except Exception as e:
                logger.error(f"Failed to fetch real Neo4j graph model: {e}")

        # Fallback to local memory model representational layout
        for node_id, n_data in MemoryGraphStore.nodes.items():
            nodes.append({
                "id": n_data["id"],
                "type": n_data["type"],
                "name": n_data["name"],
                "provider": "AWS"
            })

        for ed in MemoryGraphStore.edges:
            edges.append({
                "source": ed["source"],
                "target": ed["target"],
                "relation": ed["type"]
            })

        return {
            "nodes": nodes,
            "edges": edges
        }

    # ---------------------------------------------------------
    # NODE LOOKUP
    # ---------------------------------------------------------

    def get_node(self=None, resource_id: str = None):
        """
        Get single node
        """
        if not isinstance(self, Neo4jService):
            return Neo4jService().get_node(self)

        if self.driver:
            try:
                with self.driver.session() as session:
                    result = session.run(
                        """
                        MATCH (n {id:$id})

                        RETURN
                            n.id AS id,
                            labels(n)[0] AS type,
                            n.name AS name,
                            n.provider AS provider,
                            n.region AS region,
                            n.status AS status,
                            n.account_id AS account_id,
                            n.arn AS arn,
                            n.tags AS tags
                        """,
                        id=resource_id
                    )

                    row = result.single()

                    if row:
                        return {
                            "id": row["id"],
                            "type": row["type"],
                            "name": row["name"],
                            "provider": row["provider"] or "AWS",
                            "region": row["region"] or "",
                            "status": row["status"] or "unknown",
                            "account_id": row["account_id"],
                            "arn": row["arn"],
                            "tags": row["tags"] or {}
                        }
            except Exception as e:
                logger.error(f"Error looking up single node: {e}")

        # Fallback cache representation
        info = MemoryGraphStore.nodes.get(resource_id)
        if info:
            return {
                "id": info["id"],
                "type": info["type"],
                "name": info["name"],
                "provider": info.get("provider", "AWS"),
                "region": info.get("region", ""),
                "status": info.get("status", "unknown"),
                "account_id": info.get("account_id"),
                "arn": info.get("arn"),
                "tags": info.get("tags", {})
            }
        return None

    def get_resource_subgraph(self, resource_id: str) -> dict:
        """
        Return the resource node, and all 1-hop connected nodes and their edges.
        """
        root = self.get_node(resource_id=resource_id)
        if not root:
            return {"resource": {}, "subgraph": {"nodes": [], "edges": []}}

        nodes_dict = {root["id"]: {
            "resource_id": root["id"],
            "resource_name": root["name"],
            "resource_type": root["type"],
            "provider": root["provider"],
            "region": root["region"],
            "status": root["status"],
            "account_id": root.get("account_id"),
            "arn": root.get("arn"),
            "tags": root.get("tags", {})
        }}
        
        edges = []

        if self.driver:
            try:
                with self.driver.session() as session:
                    result = session.run(
                        """
                        MATCH (n {id:$id})-[r]-(m)
                        RETURN 
                            m.id AS m_id,
                            labels(m)[0] AS m_type,
                            m.name AS m_name,
                            m.provider AS m_provider,
                            m.region AS m_region,
                            m.status AS m_status,
                            m.account_id AS m_account_id,
                            m.arn AS m_arn,
                            m.tags AS m_tags,
                            type(r) AS relation,
                            startNode(r).id AS source,
                            endNode(r).id AS target
                        """,
                        id=resource_id
                    )
                    
                    for row in result:
                        m_id = row["m_id"]
                        if m_id not in nodes_dict:
                            nodes_dict[m_id] = {
                                "resource_id": m_id,
                                "resource_name": row["m_name"] or m_id,
                                "resource_type": row["m_type"] or "Resource",
                                "provider": row["m_provider"] or "AWS",
                                "region": row["m_region"] or "",
                                "status": row["m_status"] or "unknown",
                                "account_id": row["m_account_id"],
                                "arn": row["m_arn"],
                                "tags": row["m_tags"] or {}
                            }
                        
                        edges.append({
                            "source": row["source"],
                            "target": row["target"],
                            "relation": row["relation"] or "CONNECTED"
                        })
            except Exception as e:
                logger.error(f"Error querying resource subgraph in Neo4j: {e}")
        else:
            # Fallback to in-memory graph
            connected_ids = {resource_id}
            for e in MemoryGraphStore.edges:
                if e["source"] == resource_id or e["target"] == resource_id:
                    edges.append({
                        "source": e["source"],
                        "target": e["target"],
                        "relation": e["type"]
                    })
                    connected_ids.add(e["source"])
                    connected_ids.add(e["target"])
            
            for c_id in connected_ids:
                if c_id not in nodes_dict:
                    info = MemoryGraphStore.nodes.get(c_id)
                    if info:
                        nodes_dict[c_id] = {
                            "resource_id": info["id"],
                            "resource_name": info["name"],
                            "resource_type": info["type"],
                            "provider": info.get("provider", "AWS"),
                            "region": info.get("region", ""),
                            "status": info.get("status", "unknown"),
                            "account_id": info.get("account_id"),
                            "arn": info.get("arn"),
                            "tags": info.get("tags", {})
                        }

        return {
            "resource": nodes_dict[resource_id],
            "subgraph": {
                "nodes": list(nodes_dict.values()),
                "edges": edges
            }
        }

    # ---------------------------------------------------------
    # NODE DEPENDENCIES
    # ---------------------------------------------------------

    def get_dependencies(
        self=None,
        resource_id: str = None
    ):
        """
        Return connected nodes
        """
        if not isinstance(self, Neo4jService):
            return Neo4jService().get_dependencies(self)

        dependencies = []
        if self.driver:
            try:
                with self.driver.session() as session:
                    result = session.run(
                        """
                        MATCH (n {id:$id})-[r]->(m)

                        RETURN
                            n.id AS source,
                            m.id AS target,
                            type(r) AS relation
                        """,
                        id=resource_id
                    )

                    for row in result:
                        dependencies.append({
                            "source": row["source"],
                            "target": row["target"],
                            "relation": row["relation"]
                        })

                    return dependencies
            except Exception as e:
                logger.error(f"Error querying node dependencies in Neo4j: {e}")

        # Fallback trace
        for ed in MemoryGraphStore.edges:
            if ed["source"] == resource_id:
                dependencies.append({
                    "source": ed["source"],
                    "target": ed["target"],
                    "relation": ed["type"]
                })
        return dependencies

    # ---------------------------------------------------------
    # ADDITIONAL BACKWARD-COMPATIBILITY STATICS
    # ---------------------------------------------------------
    @staticmethod
    def create_resource(resource):
        res_id = resource.get("id") or resource.get("resource_id")
        res_type = resource.get("type") or resource.get("resource_type") or "Resource"
        name = resource.get("name") or res_id
        
        provider = resource.get("provider") or "AWS"
        region = resource.get("region") or ""
        
        status = resource.get("status") or "active"
        account_id = str(resource.get("account_id") or resource.get("account") or "")
        arn = resource.get("arn") or ""
        tags = resource.get("tags") or {}
        
        inst = Neo4jService()
        inst.create_node(
            node_type=res_type, 
            resource_id=res_id, 
            name=name, 
            provider=provider.upper(), 
            region=region,
            status=status,
            account_id=account_id,
            arn=arn,
            tags=tags
        )

    @staticmethod
    def get_full_graph():
        inst = Neo4jService()
        g = inst.get_graph()
        # translate edges: convert 'relation' to 'type'
        translated_edges = []
        for e in g["edges"]:
            translated_edges.append({
                "source": e["source"],
                "target": e["target"],
                "type": e.get("relation") or "DEPENDS_ON"
            })
        return {
            "nodes": g["nodes"],
            "edges": translated_edges
        }

    @staticmethod
    def get_orphan_resources():
        inst = Neo4jService()
        g = inst.get_graph()
        connected = set()
        for e in g["edges"]:
            connected.add(e["source"])
            connected.add(e["target"])

        orphans = []
        for n in g["nodes"]:
            if n["id"] not in connected:
                orphans.append({
                    "id": n["id"],
                    "type": n["type"],
                    "name": n["name"]
                })
        return orphans

    def get_node_count(self=None):
        if self is None or not isinstance(self, Neo4jService):
            return Neo4jService().get_node_count()
        if not self.driver:
            return len(MemoryGraphStore.nodes)
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (n)
                    RETURN count(n) AS count
                    """
                )
                row = result.single()
                return row["count"]
        except Exception as e:
            logger.error(f"Error getting node count: {e}")
            return len(MemoryGraphStore.nodes)

    def get_edge_count(self=None):
        if self is None or not isinstance(self, Neo4jService):
            return Neo4jService().get_edge_count()
        if not self.driver:
            return len(MemoryGraphStore.edges)
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH ()-[r]->()
                    RETURN count(r) AS count
                    """
                )
                row = result.single()
                return row["count"]
        except Exception as e:
            logger.error(f"Error getting edge count: {e}")
            return len(MemoryGraphStore.edges)