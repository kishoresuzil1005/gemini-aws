"""Unit tests for ResourceProvider."""

import pytest
from unittest.mock import MagicMock

from ..resource_provider import ResourceProvider
from ...resolved_resource import ResolvedResource
from ...request import ContextRequest
from ...enums import ContextLevel


@pytest.fixture
def provider():
    return ResourceProvider()


@pytest.fixture
def resource():
    r = MagicMock(spec=ResolvedResource)
    r.resource_id = "i-0abc123"
    return r


@pytest.fixture
def request_basic():
    return ContextRequest(identifier="i-0abc123", level=ContextLevel.BASIC)


class TestResourceProvider:
    def test_name(self, provider):
        assert provider.name == "resource"

    def test_output_key(self, provider):
        assert provider.output_key == "resource"

    def test_priority(self, provider):
        assert provider.priority == 0

    def test_supports_all_levels(self, provider):
        for level in ContextLevel:
            assert provider.supports(level) is True

    @pytest.mark.asyncio
    async def test_fetch_returns_standard_envelope(self, provider, resource, request_basic):
        result = await provider.fetch(resource, request_basic)
        assert "metadata" in result
        assert "data" in result

    @pytest.mark.asyncio
    async def test_fetch_metadata_fields(self, provider, resource, request_basic):
        result = await provider.fetch(resource, request_basic)
        meta = result["metadata"]
        assert meta["provider"] == "resource"
        assert meta["status"] == "ok"
        assert meta["enabled"] is True
        assert "generated_at" in meta
        assert "execution_time_ms" in meta

    @pytest.mark.asyncio
    async def test_fetch_data_contains_id(self, provider, resource, request_basic):
        result = await provider.fetch(resource, request_basic)
        assert result["data"]["id"] == "i-0abc123"
