from typing import List, Dict
from app.services.ai.assistant.knowledge_graph.models.knowledge_models import CloudNode, CloudEdge
from app.services.ai.assistant.multicloud.multicloud_models import CloudProvider

class BaseGraphBuilder:
    def build_nodes(self) -> List[CloudNode]:
        raise NotImplementedError
        
    def build_edges(self) -> List[CloudEdge]:
        raise NotImplementedError

from app.services.ai.assistant.knowledge_graph.core.graph_repository import GraphRepository
from app.services.ai.assistant.knowledge_graph.core.graph_validator import GraphValidator
from app.services.ai.assistant.knowledge_graph.core.graph_merger import GraphMerger
from app.services.ai.assistant.knowledge_graph.core.graph_indexer import GraphIndexer
from app.services.ai.assistant.knowledge_graph.intelligence.relationship_engine import RelationshipEngine
import logging

logger = logging.getLogger(__name__)

class GraphBuilderCoordinator:
    """Coordinates the full pipeline: Builders -> Validator -> Merger -> Indexer -> Repository."""
    
    def __init__(self, repository: GraphRepository, validator: GraphValidator, merger: GraphMerger, indexer: GraphIndexer, relationship_engine: RelationshipEngine):
        self._builders: Dict[CloudProvider, BaseGraphBuilder] = {}
        self.repository = repository
        self.validator = validator
        self.merger = merger
        self.indexer = indexer
        self.relationship_engine = relationship_engine
        
    def register_builder(self, provider: CloudProvider, builder: BaseGraphBuilder):
        self._builders[provider] = builder
        
    def build_graph(self):
        """Executes the pipeline."""
        logger.info("Executing Graph Build Pipeline...")
        
        all_nodes = []
        all_edges = []
        
        # 1. Builders
        for provider, builder in self._builders.items():
            nodes = builder.build_nodes()
            edges = builder.build_edges()
            all_nodes.extend(nodes)
            all_edges.extend(edges)
            
        # 2. Relationship Engine (Infer edges)
        inferred_edges = self.relationship_engine.infer_relationships(all_nodes)
        all_edges.extend(inferred_edges)
        
        # Save to temp memory or repository
        self.repository.clear()
        for n in all_nodes:
            self.repository.save_node(n)
        for e in all_edges:
            self.repository.save_edge(e)
            
        # 3. Validator
        self.validator.validate()
        
        # 4. Merger
        self.merger.merge()
        
        # 5. Indexer
        self.indexer.build_indexes()
        
        logger.info("Graph pipeline successfully generated.")
