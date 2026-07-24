"""
Thread-safe, scalable Analyzer Registry supporting multi-dimensional queries.
"""
import threading
import logging
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from app.services.ai.analyzers.base.base_analyzer import BaseAnalyzer
from app.services.ai.analyzers.base.analyzer_models import (
    CloudProvider, AnalyzerCategory, AnalyzerCapability, SupportedResource, ExecutionMode
)
from app.services.ai.analyzers.base.exceptions import AnalyzerRegistrationException

logger = logging.getLogger(__name__)


class AnalyzerQuery(BaseModel):
    """
    Query object used to filter analyzers in the registry.
    Any field left as None is ignored during filtering.
    """
    cloud: Optional[CloudProvider] = Field(default=None)
    category: Optional[AnalyzerCategory] = Field(default=None)
    capability: Optional[AnalyzerCapability] = Field(default=None)
    resource: Optional[SupportedResource] = Field(default=None)
    execution_mode: Optional[ExecutionMode] = Field(default=None)
    enabled_only: bool = Field(default=True)
    min_priority: Optional[int] = Field(default=None)


class AnalyzerRegistry:
    """
    Enterprise-grade registry for storing and querying Analyzer instances.
    Thread-safe implementation with a generic query interface.
    """
    _instance: Optional['AnalyzerRegistry'] = None
    _lock = threading.Lock()

    def __new__(cls) -> 'AnalyzerRegistry':
        """Singleton pattern for global state."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(AnalyzerRegistry, cls).__new__(cls)
                cls._instance._analyzers = {}
                cls._instance._registry_lock = threading.RLock()
        return cls._instance

    def register(self, analyzer: BaseAnalyzer, overwrite: bool = False) -> None:
        """
        Registers an analyzer instance.
        """
        analyzer_id = analyzer.metadata.id
        with self._registry_lock:
            if analyzer_id in self._analyzers and not overwrite:
                raise AnalyzerRegistrationException(f"Analyzer with ID '{analyzer_id}' is already registered.")
            
            if not analyzer.health():
                logger.warning(f"Registering analyzer '{analyzer_id}' which reports unhealthy status.")
                
            self._analyzers[analyzer_id] = analyzer
            logger.info(f"Registered analyzer: {analyzer_id} (Version: {analyzer.version()})")

    def unregister(self, analyzer_id: str) -> None:
        """Unregisters an analyzer by ID."""
        with self._registry_lock:
            if analyzer_id in self._analyzers:
                del self._analyzers[analyzer_id]
                logger.info(f"Unregistered analyzer: {analyzer_id}")

    def exists(self, analyzer_id: str) -> bool:
        """Checks if an analyzer exists."""
        with self._registry_lock:
            return analyzer_id in self._analyzers

    def get(self, analyzer_id: str) -> Optional[BaseAnalyzer]:
        """Retrieves an analyzer by ID."""
        with self._registry_lock:
            return self._analyzers.get(analyzer_id)

    def list(self) -> List[BaseAnalyzer]:
        """Retrieves all registered analyzers."""
        with self._registry_lock:
            return list(self._analyzers.values())

    def query(self, q: AnalyzerQuery) -> List[BaseAnalyzer]:
        """
        Filters registered analyzers based on the multi-dimensional query.
        
        Args:
            q (AnalyzerQuery): The filter parameters.
            
        Returns:
            List[BaseAnalyzer]: Matching analyzers.
        """
        results = []
        with self._registry_lock:
            for analyzer in self._analyzers.values():
                meta = analyzer.metadata
                
                if q.enabled_only and not meta.enabled:
                    continue
                if q.cloud and q.cloud not in meta.supported_clouds:
                    continue
                if q.category and q.category != meta.category:
                    continue
                if q.capability and q.capability not in meta.supported_capabilities:
                    continue
                if q.resource and q.resource not in meta.supported_resources:
                    continue
                if q.execution_mode and q.execution_mode != meta.execution_mode:
                    continue
                if q.min_priority and meta.priority < q.min_priority:
                    continue
                    
                results.append(analyzer)
                
        return results
