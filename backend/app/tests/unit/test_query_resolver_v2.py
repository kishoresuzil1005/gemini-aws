import pytest
from unittest.mock import patch, MagicMock

from app.services.ai.assistant.query_resolver import QueryResolver
from app.services.ai.assistant.assistant_models import ExecutionContext
from app.services.ai.assistant.resolver.candidate_generator import CandidateGenerator


@pytest.fixture
def mock_postgres():
    with patch("app.services.ai.assistant.resolver.candidate_generator.ResourceResolver") as MockClass:
        mock_instance = MagicMock()
        MockClass.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_neo4j():
    with patch("app.services.ai.assistant.resolver.candidate_generator.Neo4jService") as MockClass:
        mock_instance = MagicMock()
        MockClass.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_cache():
    with patch("app.services.ai.assistant.resolver.candidate_generator.OrchestratorCache") as MockClass:
        mock_instance = MagicMock()
        MockClass.return_value = mock_instance
        mock_instance.get.return_value = None
        yield mock_instance


def test_resolver_exact_id(mock_postgres, mock_neo4j, mock_cache):
    mock_postgres.find_candidates.return_value = [{"id": "i-0123456789abcdef0", "name": "web-prod", "type": ["AWSResource", "EC2"]}]
    resolver = QueryResolver()
    context = ExecutionContext(user_message="Analyze EC2 i-0123456789abcdef0", session_id="test")
    
    result = resolver.resolve(context)
    
    assert result.identifier == "i-0123456789abcdef0"
    assert result.confidence >= 95
    # Neo4j fallback should NOT be called
    mock_neo4j.query.assert_not_called()

def test_resolver_exact_arn(mock_postgres, mock_neo4j, mock_cache):
    mock_postgres.find_candidates.return_value = [{"id": "arn:aws:ec2:us-east-1:123:instance/i-1234", "name": "db", "type": ["EC2"]}]
    resolver = QueryResolver()
    context = ExecutionContext(user_message="Analyze arn:aws:ec2:us-east-1:123:instance/i-1234", session_id="test")
    result = resolver.resolve(context)
    assert result.identifier == "arn:aws:ec2:us-east-1:123:instance/i-1234"
    mock_neo4j.query.assert_not_called()

def test_resolver_exact_name(mock_postgres, mock_neo4j, mock_cache):
    mock_postgres.find_candidates.return_value = [{"id": "i-9999", "name": "web-server-prod", "type": ["EC2"]}]
    resolver = QueryResolver()
    context = ExecutionContext(user_message="Analyze web-server-prod", session_id="test")
    result = resolver.resolve(context)
    assert result.identifier == "i-9999"

def test_resolver_partial_name(mock_postgres, mock_neo4j, mock_cache):
    mock_postgres.find_candidates.return_value = [{"id": "i-9999", "name": "my-web-server-prod", "type": ["EC2"]}]
    resolver = QueryResolver()
    context = ExecutionContext(user_message="Analyze web-server", session_id="test")
    result = resolver.resolve(context)
    assert result.identifier == "i-9999"

def test_resolver_tag_lookup(mock_postgres, mock_neo4j, mock_cache):
    mock_postgres.find_candidates.return_value = [{"id": "i-tag", "name": "tagged-instance", "type": ["EC2"]}]
    resolver = QueryResolver()
    context = ExecutionContext(user_message="Analyze resources with env:prod", session_id="test")
    result = resolver.resolve(context)
    assert result.identifier == "i-tag"

def test_resolver_cache_hit(mock_postgres, mock_neo4j, mock_cache):
    mock_cache.get.return_value = {"id": "vpc-cache", "name": "cached-vpc", "type": ["VPC"], "score": 0.99}
    resolver = QueryResolver()
    context = ExecutionContext(user_message="Analyze cached-vpc", session_id="test-cache")
    result = resolver.resolve(context)
    assert result.identifier == "vpc-cache"
    mock_postgres.find_candidates.assert_not_called()

def test_resolver_cache_miss(mock_postgres, mock_neo4j, mock_cache):
    mock_cache.get.return_value = None
    mock_postgres.find_candidates.return_value = [{"id": "vpc-miss", "name": "miss-vpc", "type": ["VPC"]}]
    resolver = QueryResolver()
    context = ExecutionContext(user_message="Analyze miss-vpc", session_id="test-miss")
    result = resolver.resolve(context)
    assert result.identifier == "vpc-miss"
    assert mock_postgres.find_candidates.called

def test_resolver_neo4j_fallback(mock_postgres, mock_neo4j, mock_cache):
    mock_postgres.find_candidates.return_value = []
    mock_neo4j.query.return_value = [{"id": "vpc-neo4j", "name": "neo4j-vpc", "type": ["VPC"]}]
    resolver = QueryResolver()
    context = ExecutionContext(user_message="Analyze neo4j-vpc", session_id="test-fallback")
    result = resolver.resolve(context)
    assert result.identifier == "vpc-neo4j"
    assert mock_neo4j.query.called

def test_resolver_unknown_resource(mock_postgres, mock_neo4j, mock_cache):
    mock_postgres.find_candidates.return_value = []
    mock_neo4j.query.return_value = []
    resolver = QueryResolver()
    context = ExecutionContext(user_message="Analyze unknown-xyz", session_id="test")
    result = resolver.resolve(context)
    assert result.identifier is None
    assert result.ambiguity is False

def test_resolver_wrong_region(mock_postgres, mock_neo4j, mock_cache):
    # Missing region shouldn't crash
    mock_postgres.find_candidates.return_value = []
    resolver = QueryResolver()
    context = ExecutionContext(user_message="Analyze unknown in us-west-1", session_id="test")
    result = resolver.resolve(context)
    assert result.identifier is None

def test_resolver_wrong_account(mock_postgres, mock_neo4j, mock_cache):
    mock_postgres.find_candidates.return_value = []
    resolver = QueryResolver()
    context = ExecutionContext(user_message="Analyze unknown in account 12345", session_id="test")
    result = resolver.resolve(context)
    assert result.identifier is None

def test_resolver_wrong_resource_type(mock_postgres, mock_neo4j, mock_cache):
    mock_postgres.find_candidates.return_value = []
    resolver = QueryResolver()
    context = ExecutionContext(user_message="Analyze unknown lambda", session_id="test")
    result = resolver.resolve(context)
    assert result.identifier is None

def test_resolver_duplicate_resources(mock_postgres, mock_neo4j, mock_cache):
    mock_postgres.find_candidates.return_value = [
        {"id": "i-dup1", "name": "duplicate", "type": ["EC2"]},
        {"id": "i-dup2", "name": "duplicate", "type": ["EC2"]}
    ]
    resolver = QueryResolver()
    context = ExecutionContext(user_message="Analyze duplicate", session_id="test")
    result = resolver.resolve(context)
    assert result.ambiguity is True
    assert len(result.suggestions) == 2

def test_resolver_clarification_flow(mock_postgres, mock_neo4j, mock_cache):
    mock_postgres.find_candidates.return_value = [
        {"id": "i-ambig1", "name": "ambig", "type": ["EC2"]},
        {"id": "i-ambig2", "name": "ambig", "type": ["EC2"]}
    ]
    resolver = QueryResolver()
    context = ExecutionContext(user_message="Analyze ambig", session_id="test")
    result = resolver.resolve(context)
    assert result.ambiguity is True

def test_resolver_empty_query(mock_postgres, mock_neo4j, mock_cache):
    resolver = QueryResolver()
    context = ExecutionContext(user_message="", session_id="test")
    result = resolver.resolve(context)
    assert result.identifier is None

def test_resolver_null_query(mock_postgres, mock_neo4j, mock_cache):
    resolver = QueryResolver()
    # Pydantic usually prevents null, but we test graceful handling
    context = ExecutionContext(user_message=" ", session_id="test")
    result = resolver.resolve(context)
    assert result.identifier is None

def test_resolver_large_query(mock_postgres, mock_neo4j, mock_cache):
    mock_postgres.find_candidates.return_value = [{"id": "i-large", "name": "large", "type": ["EC2"]}]
    resolver = QueryResolver()
    context = ExecutionContext(user_message="Analyze large " * 100, session_id="test")
    result = resolver.resolve(context)
    assert result.identifier == "i-large"

def test_resolver_special_characters(mock_postgres, mock_neo4j, mock_cache):
    mock_postgres.find_candidates.return_value = [{"id": "i-spec!al", "name": "spec!al", "type": ["EC2"]}]
    resolver = QueryResolver()
    context = ExecutionContext(user_message="Analyze spec!al", session_id="test")
    result = resolver.resolve(context)
    assert result.identifier == "i-spec!al"

def test_resolver_mixed_case(mock_postgres, mock_neo4j, mock_cache):
    mock_postgres.find_candidates.return_value = [{"id": "i-MiXeD", "name": "MiXeD", "type": ["EC2"]}]
    resolver = QueryResolver()
    context = ExecutionContext(user_message="Analyze mIxEd", session_id="test")
    result = resolver.resolve(context)
    assert result.identifier == "i-MiXeD"
