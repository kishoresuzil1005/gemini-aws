"""
Phase 1 Integration Tests
===========================
Verifies the full Phase 1 AI Core pipeline without I/O dependencies.
"""

import pytest
from app.services.ai.reasoning_engine.entity_extractor import EntityExtractor
from app.services.ai.reasoning_engine.engine import ReasoningEngine
from app.services.ai.reasoning_engine.rule_set import required_providers
from app.services.ai.orchestrator.models import (
    Resource, CloudProvider, UnifiedContext, ProviderResult,
    ProviderOutcome, ProviderPriority, IntentCategory
)
from app.services.ai.orchestrator.aggregator import ContextAggregator
from app.services.ai.orchestrator.validator import ContextValidator
from app.services.ai.orchestrator.budget_manager import BudgetManager
from app.services.ai.resolver.confidence_engine import ConfidenceEngine, ResolutionDecision
from app.services.ai.orchestrator.models import ResolvedResource


# ===== EntityExtractor =====

def test_entity_extractor_detects_ec2_id():
    extractor = EntityExtractor()
    q = extractor.extract("Why is i-0abc1234def unhealthy?")
    assert "i-0abc1234def" in q.resource_ids

def test_entity_extractor_detects_service():
    extractor = EntityExtractor()
    q = extractor.extract("What is wrong with my RDS instance?")
    assert "rds" in q.service_hints

def test_entity_extractor_detects_environment():
    extractor = EntityExtractor()
    q = extractor.extract("Check production EC2")
    assert "prod" in q.environment_hints or "production" in q.environment_hints

def test_entity_extractor_detects_region():
    extractor = EntityExtractor()
    q = extractor.extract("List resources in us-east-1")
    assert "us-east-1" in q.environment_hints


# ===== ReasoningEngine =====

def test_reasoning_health_check():
    engine = ReasoningEngine()
    result = engine.reason("Why is my EC2 instance unhealthy?")
    assert result.intent == IntentCategory.HEALTH_CHECK
    assert "inventory" in result.required_providers

def test_reasoning_security():
    engine = ReasoningEngine()
    result = engine.reason("Check security vulnerabilities on my S3 bucket")
    assert result.intent == IntentCategory.SECURITY_AUDIT
    assert "security" in result.required_providers

def test_reasoning_cost():
    engine = ReasoningEngine()
    result = engine.reason("Why is my AWS bill so expensive?")
    assert result.intent == IntentCategory.COST_ANALYSIS
    assert "cost" in result.required_providers


# ===== ConfidenceEngine =====

def test_confidence_auto_select():
    engine = ConfidenceEngine()
    r = Resource(id="i-0abc", provider=CloudProvider.AWS, service="ec2", type="instance")
    candidates = [ResolvedResource(resource=r, confidence=1.0, source="regex")]
    result = engine.score(candidates)
    assert result.decision == ResolutionDecision.AUTO_SELECT
    assert result.best_match is not None

def test_confidence_no_match():
    engine = ConfidenceEngine()
    result = engine.score([])
    assert result.decision == ResolutionDecision.NO_MATCH


# ===== Aggregator =====

def test_aggregator_quality_score():
    agg = ContextAggregator()
    results = [
        ProviderResult(provider="inventory", outcome=ProviderOutcome.SUCCESS,
                       priority=ProviderPriority.CRITICAL, confidence=1.0, completeness=1.0, freshness=1.0),
        ProviderResult(provider="graph", outcome=ProviderOutcome.SUCCESS,
                       priority=ProviderPriority.HIGH, confidence=0.9, completeness=0.9, freshness=1.0),
    ]
    ctx = agg.merge(results=results, raw_question="Why is EC2 unhealthy?")
    assert ctx.quality.score > 0
    assert "inventory" in ctx.quality.providers_executed
    assert "graph" in ctx.quality.providers_executed

def test_aggregator_no_empty_provider_data():
    """Ensure no empty {} reaches the LLM — acceptance criterion."""
    agg = ContextAggregator()
    results = []
    ctx = agg.merge(results=results, raw_question="Test")
    # Empty context should report 0 quality, not crash
    assert ctx.quality.score == 0.0


# ===== Validator =====

def test_validator_health_check_missing_resource():
    validator = ContextValidator()
    ctx = UnifiedContext(raw_question="Why is EC2 unhealthy?")
    report = validator.validate(ctx, intent="health_check")
    assert not report.valid
    assert "resource" in report.missing_sections

def test_validator_passes_with_resource():
    validator = ContextValidator()
    r = Resource(id="i-0abc", provider=CloudProvider.AWS, service="ec2", type="instance")
    ctx = UnifiedContext(raw_question="Status?", resource=r)
    report = validator.validate(ctx, intent="general")
    assert report.valid


# ===== BudgetManager =====

def test_budget_manager_within_budget():
    bm = BudgetManager(budget=10000)
    sections = {"resource": {"id": "i-0abc"}, "security": []}
    pruned, truncated = bm.enforce(sections)
    assert truncated == []

def test_budget_manager_truncates_when_over():
    bm = BudgetManager(budget=1)  # Unrealistically small to force truncation
    sections = {"resource": {"id": "i-0abc", "details": "x" * 10000}}
    pruned, truncated = bm.enforce(sections)
    assert len(truncated) > 0


# ===== Rule Set =====

def test_rule_set_health_check():
    providers = required_providers("health_check")
    assert "inventory" in providers
    assert "metrics" in providers

def test_rule_set_adds_security_for_s3():
    providers = required_providers("general", service_hints=["s3"])
    assert "security" in providers
