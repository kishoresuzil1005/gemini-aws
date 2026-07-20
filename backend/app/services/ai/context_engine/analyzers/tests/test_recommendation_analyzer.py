"""Unit tests for RecommendationAnalyzer."""

import pytest
from ..recommendation_analyzer import RecommendationAnalyzer
from ...models import AIContext


@pytest.fixture
def analyzer():
    return RecommendationAnalyzer()


class TestRecommendationAnalyzer:
    def test_name(self, analyzer):
        assert analyzer.name == "recommendation"

    def test_analyze_returns_dict(self, analyzer):
        ctx    = AIContext()
        result = analyzer.analyze(ctx)
        assert isinstance(result, dict)

    def test_generate_returns_list(self, analyzer):
        ctx    = AIContext()
        result = analyzer.generate(ctx)
        assert isinstance(result, list)

    def test_stub_status(self, analyzer):
        ctx    = AIContext()
        result = analyzer.analyze(ctx)
        assert result["status"] == "not_implemented"
