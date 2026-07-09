import json
from typing import Dict, Any

from app.services.ai.core.context.intent_classifier import IntentClassifier
from app.services.ai.core.context.graph_retriever import GraphRetriever
from app.services.ai.core.context.metadata_retriever import MetadataRetriever
from app.services.ai.core.context.document_retriever import DocumentRetriever


class ContextBuilder:

    def __init__(self):

        self.intent = IntentClassifier()

        self.graph = GraphRetriever()

        self.metadata = MetadataRetriever()

        self.docs = DocumentRetriever()

    def close(self):

        self.graph.close()

        self.metadata.close()

    def build(
        self,
        question: str
    ) -> Dict[str, Any]:

        intent_result = self.intent.classify(question)

        # Extract resource IDs from classified resources
        entities = [
            r.resource_id
            for r in intent_result.resources
            if r.resource_id
        ]

        # Gather graph topology and metadata per entity
        resources = []

        for entity in entities:

            graph = self.graph.get_neighbors(entity)

            metadata = self.metadata.get_resource(entity)

            resources.append(
                {
                    "resource_id": entity,
                    "graph": graph,
                    "metadata": metadata
                }
            )

        # Retrieve relevant documentation from Qdrant
        documents = self.docs.search(question, limit=5)

        return {
            "question": question,
            "intent": intent_result.intent.value,
            "confidence": intent_result.confidence,
            "action": intent_result.action,
            "entities": entities,
            "graph": [r["graph"] for r in resources],
            "metadata": [r["metadata"] for r in resources],
            "resources": resources,
            "documents": documents
        }
