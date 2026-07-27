"""
AI Context Orchestrator — Core Engine
=======================================
Entry point for the new AI pipeline.
Activated only when ENABLE_NEW_ORCHESTRATOR feature flag is True.

Pipeline:
  IntentEngine → EntityExtractor → MultiSourceResolver → ConfidenceEngine
       → ToolPlanner → ParallelProviders (asyncio DAG)
       → Aggregator → Validator → BudgetManager → PromptBuilder → LLM
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

from .aggregator import ContextAggregator
from .budget_manager import BudgetManager
from .cache import OrchestratorCache
from .exceptions import OrchestratorError, ResolutionError, ValidationError
from .feature_flag_util import is_enabled
from .models import (
    IntentCategory,
    ProviderOutcome,
    ProviderResult,
    ReasoningResult,
    UnifiedContext,
)
from .provider_registry import ProviderRegistry
from .telemetry import (
    track_orchestrator_latency,
    track_provider_latency,
    record_resolution,
)
from .validator import ContextValidator

logger = logging.getLogger(__name__)

_DEFAULT_PROVIDER_TIMEOUT = 5.0   # seconds
_QUALITY_TARGET = 0.75            # early-exit threshold


class Orchestrator:
    """
    Main orchestrator.  Coordinates all subsystems.

    Usage:
        orch = Orchestrator()
        context = await orch.process(question="Why is EC2 i-0abc unhealthy?")
    """

    def __init__(
        self,
        budget: int = 3000,
        provider_timeout: float = _DEFAULT_PROVIDER_TIMEOUT,
        quality_target: float = _QUALITY_TARGET,
    ):
        if not is_enabled("ENABLE_NEW_ORCHESTRATOR"):
            raise OrchestratorError(
                "Orchestrator is disabled. Set ENABLE_NEW_ORCHESTRATOR: true in feature_flags.yaml"
            )

        self.registry = ProviderRegistry.get_instance()
        self.aggregator = ContextAggregator()
        self.validator = ContextValidator()
        self.budget_manager = BudgetManager(budget=budget)
        self.cache = OrchestratorCache()
        self.provider_timeout = provider_timeout
        self.quality_target = quality_target

        logger.info(
            "[Orchestrator] Initialised | budget=%d tokens | timeout=%.1fs | quality=%.2f",
            budget, provider_timeout, quality_target,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def process(
        self,
        question: str,
        session_id: Optional[str] = None,
        intent: Optional[str] = None,
    ) -> UnifiedContext:
        """
        Full async pipeline: question → UnifiedContext ready for prompt building.

        Args:
            question:   Raw user question.
            session_id: Conversation / investigation ID for cache isolation.
            intent:     Override intent classification (useful for tests).
        Returns:
            A validated UnifiedContext.
        """
        with track_orchestrator_latency(intent or "unknown"):
            start = time.perf_counter()

            # 1. Resolve intent
            resolved_intent = intent or IntentCategory.GENERAL.value

            # 2. Get providers ordered by priority
            registrations = self.registry.list_for_intent(resolved_intent)
            provider_names = [r.name for r in registrations]
            logger.info("[Orchestrator] Providers selected: %s", provider_names)

            # 3. Run providers in parallel with timeout + early exit
            results = await self._run_providers(registrations, question, session_id)

            # 4. Aggregate
            context = self.aggregator.merge(
                results=results,
                raw_question=question,
                session_id=session_id,
            )

            # 5. Validate
            report = self.validator.validate(context, intent=resolved_intent)
            if not report.valid:
                logger.error("[Orchestrator] Validation failed: %s", report.missing_sections)

            elapsed = time.perf_counter() - start
            logger.info("[Orchestrator] Pipeline complete in %.3fs | quality=%.2f", elapsed, context.quality.score)
            record_resolution(success=report.valid)

            return context

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _run_providers(
        self,
        registrations,
        question: str,
        session_id: Optional[str],
    ) -> List[ProviderResult]:
        """Run all registered providers concurrently with timeout and early exit."""
        results: List[ProviderResult] = []

        tasks = []
        for reg in registrations:
            tasks.append(self._run_single_provider(reg, question, session_id))

        gathered = await asyncio.gather(*tasks, return_exceptions=True)

        for reg, outcome in zip(registrations, gathered):
            if isinstance(outcome, Exception):
                results.append(ProviderResult(
                    provider=reg.name,
                    outcome=ProviderOutcome.ERROR,
                    priority=reg.priority,
                    error=str(outcome),
                ))
            else:
                results.append(outcome)

            # Early exit check after each provider
            partial_ctx = self.aggregator.merge(results=results, raw_question=question)
            if partial_ctx.quality.score >= self.quality_target:
                logger.info(
                    "[Orchestrator] Quality target %.2f reached after %d providers — skipping remaining.",
                    self.quality_target, len(results),
                )
                break

        return results

    async def _run_single_provider(
        self,
        registration,
        question: str,
        session_id: Optional[str],
    ) -> ProviderResult:
        """Instantiate and call a single provider with a timeout."""
        provider_name = registration.name
        with track_provider_latency(provider_name):
            try:
                provider = registration.factory()
                coro = provider.run(question=question, session_id=session_id)
                result: ProviderResult = await asyncio.wait_for(
                    coro, timeout=self.provider_timeout
                )
                result.provider = provider_name
                return result
            except asyncio.TimeoutError:
                logger.warning("[Orchestrator] Provider '%s' timed out", provider_name)
                return ProviderResult(
                    provider=provider_name,
                    outcome=ProviderOutcome.TIMEOUT,
                    priority=registration.priority,
                    error=f"Timed out after {self.provider_timeout}s",
                )
            except Exception as exc:
                logger.error("[Orchestrator] Provider '%s' error: %s", provider_name, exc)
                return ProviderResult(
                    provider=provider_name,
                    outcome=ProviderOutcome.ERROR,
                    priority=registration.priority,
                    error=str(exc),
                )
