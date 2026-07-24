"""
Security Engine.
Executes SecurityRules over the GraphIndex deterministically.
"""
import logging
from typing import List
from app.services.ai.analyzers.engines.context.engine_context import EngineContext
from app.services.ai.analyzers.engines.graph.graph_index import GraphIndex
from app.services.ai.analyzers.engines.security.security_registry import SecurityRuleRegistry
from app.services.ai.analyzers.engines.security.security_models import SecurityFinding
from app.services.ai.analyzers.engines.telemetry.metrics import record_metrics

logger = logging.getLogger(__name__)

class SecurityEngine:
    
    @classmethod
    def version(cls) -> str:
        return "1.0.0"
        
    @staticmethod
    @record_metrics("SecurityEngine")
    def analyze(context: EngineContext, index: GraphIndex, registry: SecurityRuleRegistry) -> List[SecurityFinding]:
        """
        Executes rules across the graph natively in O(V) time.
        """
        findings = []
        
        # Instead of scanning every node against every rule, 
        # we iterate over the rule types and use GraphIndex.by_type to instantly fetch targets.
        
        # Determine all unique types present in the graph
        available_types = index.by_type.keys()
        
        for n_type in available_types:
            # Fetch rules that explicitly support this node type
            rules = registry.get_rules_for_node(n_type)
            if not rules:
                continue
                
            # Fetch nodes of this type
            node_ids = index.by_type[n_type]
            
            for node_id in node_ids:
                for rule in rules:
                    try:
                        finding = rule.evaluate(node_id, context.graph, context)
                        if finding:
                            findings.append(finding)
                    except Exception as e:
                        logger.error(f"Rule {rule.metadata().id} failed on node {node_id}: {e}")
                        
        return findings
