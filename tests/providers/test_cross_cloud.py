import pytest
from app.providers.cross_cloud_discovery import CrossCloudDiscovery
from app.providers.cross_cloud_graph import CrossCloudGraphBuilder
from unittest.mock import MagicMock

def test_cross_cloud_blast_radius():
    # Setup
    mock_graph_builder = CrossCloudGraphBuilder()
    
    # Test blast radius crossing boundaries
    result = mock_graph_builder.calculate_blast_radius("k8s-pod-backend")
    
    # Assertions
    assert result["target"] == "k8s-pod-backend"
    assert "aws" in result["affected_clouds"]
    assert "azure" in result["affected_clouds"]
    assert "azure-sql-db-1" in result["critical_dependencies"]
    assert result["total_impacted_nodes"] > 0
