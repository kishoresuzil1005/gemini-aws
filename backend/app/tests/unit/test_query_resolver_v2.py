from unittest.mock import patch, MagicMock
from app.services.ai.assistant.query_resolver import QueryResolver
from app.services.ai.assistant.assistant_models import ExecutionContext

@patch("app.services.ai.assistant.resolver.candidate_generator.Neo4jService")
def test_resolver_exact_id(mock_neo4j_class):
    mock_neo4j = MagicMock()
    mock_neo4j_class.return_value = mock_neo4j
    mock_neo4j.query.return_value = [{"id": "i-0123456789abcdef0", "name": "web-prod", "type": ["AWSResource", "EC2"]}]
    
    resolver = QueryResolver()
    context = ExecutionContext(user_message="Analyze EC2 i-0123456789abcdef0", session_id="test")
    
    result = resolver.resolve(context)
    
    assert result.identifier == "i-0123456789abcdef0"
    assert result.confidence >= 0.99
    assert result.source == "candidate_pipeline_exact"


@patch("app.services.ai.assistant.resolver.candidate_generator.Neo4jService")
def test_resolver_resource_name(mock_neo4j_class):
    mock_neo4j = MagicMock()
    mock_neo4j_class.return_value = mock_neo4j
    mock_neo4j.query.return_value = [{"id": "i-9999", "name": "web-server", "type": ["AWSResource", "EC2"]}]
    
    resolver = QueryResolver()
    context = ExecutionContext(user_message="Analyze web-server", session_id="test")
    
    result = resolver.resolve(context)
    
    assert result.identifier == "i-9999"
    assert result.confidence > 0.8
    assert result.source == "candidate_pipeline"


@patch("app.services.ai.assistant.resolver.candidate_generator.Neo4jService")
def test_resolver_vpc(mock_neo4j_class):
    mock_neo4j = MagicMock()
    mock_neo4j_class.return_value = mock_neo4j
    mock_neo4j.query.return_value = [{"id": "vpc-0abc", "name": "production", "type": ["AWSResource", "VPC"]}]
    
    resolver = QueryResolver()
    context = ExecutionContext(user_message="Analyze production VPC", session_id="test")
    
    result = resolver.resolve(context)
    
    assert result.identifier == "vpc-0abc"
    assert result.confidence > 0.8


@patch("app.services.ai.assistant.resolver.candidate_generator.Neo4jService")
def test_resolver_ambiguous_query(mock_neo4j_class):
    mock_neo4j = MagicMock()
    mock_neo4j_class.return_value = mock_neo4j
    # Multiple EC2 instances
    mock_neo4j.query.return_value = [
        {"id": "i-1111", "name": "web1", "type": ["AWSResource", "EC2"]},
        {"id": "i-2222", "name": "web2", "type": ["AWSResource", "EC2"]},
    ]
    
    resolver = QueryResolver()
    context = ExecutionContext(user_message="Analyze EC2", session_id="test")
    
    result = resolver.resolve(context)
    
    assert result.ambiguity is True
    assert len(result.suggestions) == 2
    assert result.identifier is None


@patch("app.services.ai.assistant.resolver.candidate_generator.Neo4jService")
def test_resolver_unknown_resource(mock_neo4j_class):
    mock_neo4j = MagicMock()
    mock_neo4j_class.return_value = mock_neo4j
    mock_neo4j.query.return_value = []
    
    resolver = QueryResolver()
    context = ExecutionContext(user_message="Analyze server xyz123", session_id="test")
    
    result = resolver.resolve(context)
    
    assert result.identifier is None
    assert result.ambiguity is False


@patch("app.services.ai.assistant.resolver.candidate_generator.Neo4jService")
def test_resolver_conversation_memory(mock_neo4j_class):
    mock_neo4j = MagicMock()
    mock_neo4j_class.return_value = mock_neo4j
    
    resolver = QueryResolver()
    context = ExecutionContext(user_message="Restart it", session_id="test", identifier="i-9999")
    
    result = resolver.resolve(context)
    
    assert result.identifier == "i-9999"
    assert result.source == "conversation_memory"
    # Should not even call Neo4j
    mock_neo4j.query.assert_not_called()
