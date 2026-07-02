from typing import Dict

from app.ai.context.intent_classifier import IntentClassifier
from app.ai.context.inventory_context import InventoryContext
from app.ai.context.graph_context import GraphContext
from app.ai.context.monitoring_context import MonitoringContext
from app.ai.context.document_retriever import DocumentRetriever


class CloudContextBuilder:
    """
    Central orchestrator that gathers all relevant cloud information
    for a user question before sending it to the LLM.

    Combines:
      - Intent classification
      - PostgreSQL inventory
      - Neo4j graph topology
      - Monitoring metrics
      - Qdrant RAG documents
    """

    def __init__(self):

        self.intent_classifier = IntentClassifier()

        self.inventory = InventoryContext()

        self.graph = GraphContext()

        self.monitoring = MonitoringContext()

        self.documents = DocumentRetriever()

    def close(self):

        self.graph.close()

    def build(
        self,
        question: str
    ) -> Dict:

        intent = self.intent_classifier.classify(question)

        return {

            "question": question,

            "intent": intent.intent.value,

            "confidence": intent.confidence,

            "action": intent.action,

            "resources_mentioned": [
                r.resource_type.value
                for r in intent.resources
            ],

            "inventory": self.inventory.build(intent),

            "graph": self.graph.build(intent),

            "metrics": self.monitoring.build(intent),

            "documents": self.documents.search(question)
        }
