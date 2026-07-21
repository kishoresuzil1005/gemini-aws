"""Deterministic analysis lifecycle for the canonical AI context."""

import logging
from typing import Iterable

logger = logging.getLogger(__name__)

from .analyzers.architecture_analyzer import ArchitectureAnalyzer
from .analyzers.base_analyzer import BaseAnalyzer
from .analyzers.blast_radius_analyzer import BlastRadiusAnalyzer
from .analyzers.compliance_analyzer import ComplianceAnalyzer
from .analyzers.cost_analyzer import CostAnalyzer
from .analyzers.dependency_analyzer import DependencyAnalyzer
from .analyzers.performance_analyzer import PerformanceAnalyzer
from .analyzers.recommendation_analyzer import RecommendationAnalyzer
from .analyzers.security_analyzer import SecurityAnalyzer
from .models import AIContext


class AnalysisEngine:
    """Runs analyzers against data already assembled into ``AIContext``.

    Analyzers never fetch cloud data.  Provider output is the only input, and
    ``AIContext.findings``/``recommendations`` are the only analysis output.
    """

    def __init__(self, analyzers: Iterable[BaseAnalyzer] | None = None) -> None:
        self.analyzers = list(analyzers or (
            DependencyAnalyzer(),
            BlastRadiusAnalyzer(),
            ArchitectureAnalyzer(),
            SecurityAnalyzer(),
            CostAnalyzer(),
            PerformanceAnalyzer(),
            ComplianceAnalyzer(),
        ))
        self.recommendation_analyzer = RecommendationAnalyzer()

    def analyze(self, context: AIContext) -> AIContext:
        for analyzer in self.analyzers:
            result = analyzer.analyze(context)
            if result.status == "success":
                context.findings[analyzer.name] = result

        recommendations = self.recommendation_analyzer.generate(context)
        context.recommendations = recommendations
        
        logger.info("===== Findings =====")
        logger.info(context.findings.keys())
        logger.info("===== Graph after analysis =====")
        logger.info(context.graph)
        
        return context
