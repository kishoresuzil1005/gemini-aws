from neo4j import GraphDatabase
from app.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
import logging

logger = logging.getLogger("Neo4j_Driver")

try:
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD)
    )
except Exception as e:
    logger.error(f"Failed to create Neo4j driver connection: {e}")
    driver = None
