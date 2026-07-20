"""End-to-end integration test for the ContextEngine.

Tests the full pipeline:
    ContextRequest → ContextEngine → ProviderManager → Providers → Assembler → AIContext

These tests use pytest-asyncio and run against a real (or mock) backend.
They are designed to pass without live AWS credentials or a live database
by mocking the provider-level fetch() calls.

Run:
    cd backend
    venv/bin/python3.13 -m pytest app/services/ai/context_engine/tests/ -v
"""

import asyncio
import pytest
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.ai.context_engine import (
    ContextEngine,
    ContextRequest,
    ContextLevel,
    AIContext,
    register_default_providers,
)
from app.services.ai.context_engine.registry import registry, ProviderRegistry
from app.services.ai.context_engine.configuration import PipelineConfiguration
from app.services.ai.context_engine.providers import (
    ResourceProvider,
    GraphProvider,
    InventoryProvider,
)


# ─────────────────────────────────────────────────────────────────────────────
#  Fixtures
# ─────────────────────────────────────────────────────────────────────────────

MOCK_RESOURCE_ID = "i-0abc1234567890abc"


def _make_std_response(output_key: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Build a standard provider response envelope for mocking."""
    from app.services.ai.context_engine.common.helpers import iso_timestamp
    return {
        "metadata": {
            "provider":         output_key,
            "version":          "1.0",
            "generated_at":     iso_timestamp(),
            "cache_ttl":        1800,
            "status":           "ok",
            "enabled":          True,
            "execution_time_ms": 1.0,
            "source":           "mock",
        },
        "data": data,
    }


class FakeServiceContainer:
    """Mock container for DI."""
    def __init__(self):
        self.db_session_factory = MagicMock()
        self.neo4j_service = MagicMock()
        self.cloudwatch_service = MagicMock()
        self.iam_service = MagicMock()
        self.cost_service = MagicMock()
        self.documentation_service = MagicMock()

@pytest.fixture()
def fake_container():
    return FakeServiceContainer()


@pytest.fixture()
def isolated_registry():
    """Returns a fresh ProviderRegistry that is cleaned up after the test."""
    reg = ProviderRegistry()
    yield reg


@pytest.fixture()
def mock_resource_provider(fake_container):
    provider = ResourceProvider(
        db_session_factory=fake_container.db_session_factory,
        neo4j_service=fake_container.neo4j_service
    )
    provider.fetch = AsyncMock(return_value=_make_std_response("resource", {
        "id":       MOCK_RESOURCE_ID,
        "name":     "test-instance",
        "type":     "EC2",
        "provider": "aws",
        "region":   "us-east-1",
        "account":  "123456789012",
        "arn":      f"arn:aws:ec2:us-east-1:123456789012:instance/{MOCK_RESOURCE_ID}",
        "status":   "running",
        "tags":     {"Environment": "test"},
    }))
    return provider


@pytest.fixture()
def mock_graph_provider(fake_container):
    provider = GraphProvider(neo4j_service=fake_container.neo4j_service)
    provider.fetch = AsyncMock(return_value=_make_std_response("graph", {
        "resource": {"id": MOCK_RESOURCE_ID, "type": "EC2"},
        "subgraph": {
            "nodes": [{"id": MOCK_RESOURCE_ID, "type": "EC2"}, {"id": "sg-001", "type": "SecurityGroup"}],
            "edges": [{"source": MOCK_RESOURCE_ID, "target": "sg-001", "relation": "MEMBER_OF"}],
        },
    }))
    return provider


@pytest.fixture()
def mock_inventory_provider(fake_container):
    provider = InventoryProvider(db_session_factory=fake_container.db_session_factory)
    provider.fetch = AsyncMock(return_value=_make_std_response("inventory", {
        "resource_id":     MOCK_RESOURCE_ID,
        "account_id":      "123456789012",
        "organization":    "Test Org",
        "environment":     "test",
        "project":         "context-engine",
        "region":          "us-east-1",
        "provider":        "aws",
        "owner":           "platform-team",
        "tags":            {"Environment": "test"},
        "metadata":        {},
        "scanner_version": "1.0.0",
        "last_discovered": "2026-07-20T00:00:00Z",
    }))
    return provider


# ─────────────────────────────────────────────────────────────────────────────
#  Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestContextEngineEndToEnd:
    """Full pipeline tests using mocked providers."""

    @pytest.mark.asyncio
    async def test_basic_context_returns_aicontext(
        self,
        mock_resource_provider,
        mock_graph_provider,
        mock_inventory_provider,
        isolated_registry,
    ):
        """engine.build() must return a populated AIContext for BASIC level."""
        for p in [mock_resource_provider, mock_graph_provider, mock_inventory_provider]:
            isolated_registry.register(p)

        from app.services.ai.context_engine.resolver import ResourceResolver
        from app.services.ai.context_engine.cache import MemoryCache

        config = PipelineConfiguration(
            providers=isolated_registry.ordered_providers,
            cache=MemoryCache(),
            resolver=ResourceResolver(),
        )

        engine  = ContextEngine(configuration=config)
        request = ContextRequest(identifier=MOCK_RESOURCE_ID, level=ContextLevel.BASIC)
        context = await engine.build(request)

        assert isinstance(context, AIContext)

    @pytest.mark.asyncio
    async def test_resource_section_populated(
        self,
        mock_resource_provider,
        isolated_registry,
    ):
        """ctx.resource must contain id, type, provider, region, status."""
        isolated_registry.register(mock_resource_provider)

        from app.services.ai.context_engine.resolver import ResourceResolver
        from app.services.ai.context_engine.cache import MemoryCache

        config  = PipelineConfiguration(
            providers=isolated_registry.ordered_providers,
            cache=MemoryCache(),
            resolver=ResourceResolver(),
        )
        engine  = ContextEngine(configuration=config)
        request = ContextRequest(identifier=MOCK_RESOURCE_ID, level=ContextLevel.BASIC)
        context = await engine.build(request)

        assert context.resource.get("id")       == MOCK_RESOURCE_ID
        assert context.resource.get("type")     == "EC2"
        assert context.resource.get("provider") == "aws"
        assert context.resource.get("region")   == "us-east-1"
        assert context.resource.get("status")   == "running"

    @pytest.mark.asyncio
    async def test_graph_section_populated(
        self,
        mock_resource_provider,
        mock_graph_provider,
        isolated_registry,
    ):
        """ctx.graph must contain nodes, edges, and subgraph."""
        for p in [mock_resource_provider, mock_graph_provider]:
            isolated_registry.register(p)

        from app.services.ai.context_engine.resolver import ResourceResolver
        from app.services.ai.context_engine.cache import MemoryCache

        config  = PipelineConfiguration(
            providers=isolated_registry.ordered_providers,
            cache=MemoryCache(),
            resolver=ResourceResolver(),
        )
        engine  = ContextEngine(configuration=config)
        request = ContextRequest(identifier=MOCK_RESOURCE_ID, level=ContextLevel.BASIC)
        context = await engine.build(request)

        assert "subgraph" in context.graph
        assert "nodes" in context.graph["subgraph"]
        assert "edges" in context.graph["subgraph"]
        assert len(context.graph["subgraph"]["nodes"]) >= 1

    @pytest.mark.asyncio
    async def test_inventory_section_populated(
        self,
        mock_resource_provider,
        mock_inventory_provider,
        isolated_registry,
    ):
        """ctx.inventory must contain owner, environment, and project."""
        for p in [mock_resource_provider, mock_inventory_provider]:
            isolated_registry.register(p)

        from app.services.ai.context_engine.resolver import ResourceResolver
        from app.services.ai.context_engine.cache import MemoryCache

        config  = PipelineConfiguration(
            providers=isolated_registry.ordered_providers,
            cache=MemoryCache(),
            resolver=ResourceResolver(),
        )
        engine  = ContextEngine(configuration=config)
        request = ContextRequest(identifier=MOCK_RESOURCE_ID, level=ContextLevel.BASIC)
        context = await engine.build(request)

        assert context.inventory.get("owner")       == "platform-team"
        assert context.inventory.get("environment") == "test"
        assert context.inventory.get("project")     == "context-engine"

    @pytest.mark.asyncio
    async def test_metadata_stamped_correctly(
        self,
        mock_resource_provider,
        isolated_registry,
    ):
        """ctx.metadata must include schema_version, engine_version, context_level."""
        isolated_registry.register(mock_resource_provider)

        from app.services.ai.context_engine.resolver import ResourceResolver
        from app.services.ai.context_engine.cache import MemoryCache

        config  = PipelineConfiguration(
            providers=isolated_registry.ordered_providers,
            cache=MemoryCache(),
            resolver=ResourceResolver(),
        )
        engine  = ContextEngine(configuration=config)
        request = ContextRequest(identifier=MOCK_RESOURCE_ID, level=ContextLevel.STANDARD)
        context = await engine.build(request)

        assert "schema_version" in context.metadata
        assert "engine_version" in context.metadata
        assert "generated_at"   in context.metadata
        assert context.metadata.get("context_level") == "standard"

    @pytest.mark.asyncio
    async def test_execution_tracks_providers(
        self,
        mock_resource_provider,
        mock_graph_provider,
        isolated_registry,
    ):
        """ctx.execution.providers_executed must list successfully run providers."""
        for p in [mock_resource_provider, mock_graph_provider]:
            isolated_registry.register(p)

        from app.services.ai.context_engine.resolver import ResourceResolver
        from app.services.ai.context_engine.cache import MemoryCache

        config  = PipelineConfiguration(
            providers=isolated_registry.ordered_providers,
            cache=MemoryCache(),
            resolver=ResourceResolver(),
        )
        engine  = ContextEngine(configuration=config)
        request = ContextRequest(identifier=MOCK_RESOURCE_ID, level=ContextLevel.BASIC)
        context = await engine.build(request)

        executed = context.execution.providers_executed
        assert "resource" in executed
        assert "graph"    in executed

    @pytest.mark.asyncio
    async def test_provider_data_stored(
        self,
        mock_resource_provider,
        isolated_registry,
    ):
        """ctx.provider_data must store the raw provider envelope."""
        isolated_registry.register(mock_resource_provider)

        from app.services.ai.context_engine.resolver import ResourceResolver
        from app.services.ai.context_engine.cache import MemoryCache

        config  = PipelineConfiguration(
            providers=isolated_registry.ordered_providers,
            cache=MemoryCache(),
            resolver=ResourceResolver(),
        )
        engine  = ContextEngine(configuration=config)
        request = ContextRequest(identifier=MOCK_RESOURCE_ID, level=ContextLevel.BASIC)
        context = await engine.build(request)

        assert "resource" in context.provider_data

    @pytest.mark.asyncio
    async def test_empty_identifier_raises(self):
        """engine.build() must raise ValueError when identifier is empty."""
        engine  = ContextEngine()
        request = ContextRequest(identifier="", level=ContextLevel.BASIC)
        with pytest.raises(ValueError, match="identifier"):
            await engine.build(request)


class TestContextLevelFilter:
    """Verify that provider.supports() is respected for each level."""

    def test_basic_level_all_core_providers_run(self):
        from app.services.ai.context_engine.providers import (
            ResourceProvider, GraphProvider, InventoryProvider
        )
        fake_container = FakeServiceContainer()
        assert ResourceProvider(db_session_factory=fake_container.db_session_factory, neo4j_service=fake_container.neo4j_service).supports(ContextLevel.BASIC) is True
        assert GraphProvider(neo4j_service=fake_container.neo4j_service).supports(ContextLevel.BASIC) is True
        assert InventoryProvider(db_session_factory=fake_container.db_session_factory).supports(ContextLevel.BASIC) is True

    def test_iam_only_on_full_and_deep(self):
        from app.services.ai.context_engine.providers import IAMProvider
        fake_container = FakeServiceContainer()
        p = IAMProvider(iam_service=fake_container.iam_service)
        assert p.supports(ContextLevel.BASIC)    is False
        assert p.supports(ContextLevel.STANDARD) is False
        assert p.supports(ContextLevel.FULL)     is True
        assert p.supports(ContextLevel.DEEP)     is True

    def test_metrics_only_on_deep(self):
        from app.services.ai.context_engine.providers import MetricsProvider
        fake_container = FakeServiceContainer()
        p = MetricsProvider(cloudwatch_service=fake_container.cloudwatch_service)
        assert p.supports(ContextLevel.BASIC)    is False
        assert p.supports(ContextLevel.STANDARD) is False
        assert p.supports(ContextLevel.FULL)     is False
        assert p.supports(ContextLevel.DEEP)     is True
