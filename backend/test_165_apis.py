"""
Enterprise Complete API Surface Test
======================================
Runs all 165 endpoints with a mocked dependency layer to ensure no unhandled exceptions (HTTP 500).
"""

import sys
import json
import traceback
import re
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List, Optional
from fastapi.routing import APIRoute

# Mock definitions (same as test_all_endpoints.py)
class MockNeo4jService:
    def __init__(self, *args, **kwargs):
        self.driver = None
    def close(self): pass
    def health_check(self): return {"status": "mock", "connected": False}
    def node_exists(self, resource_id: str) -> bool: return False
    def query(self, query: str, **kwargs): return []
    def clear_graph(self): pass
    def create_node(self, *args, **kwargs): return None
    def create_relationship(self, *args, **kwargs): return None
    def get_graph(self, region: str = None) -> Dict[str, Any]: return {"nodes": [], "edges": []}
    def get_node(self, resource_id: str = None) -> Optional[Dict[str, Any]]: return None
    def get_resource_subgraph(self, resource_id: str) -> Dict[str, Any]: return {"nodes": [], "edges": []}
    def get_dependencies(self, resource_id: str) -> List[Dict[str, Any]]: return []
    def get_full_graph(self) -> Dict[str, Any]: return {"nodes": [], "edges": []}
    def get_orphan_resources(self) -> List[Dict[str, Any]]: return []
    def get_node_count(self) -> int: return 0
    def get_edge_count(self) -> int: return 0

class MockKnowledgeClient:
    def get_resource(self, resource_id: str) -> Optional[Dict[str, Any]]:
        return {"id": resource_id, "type": "EC2", "name": f"mock-{resource_id}", "region": "us-east-1", "status": "running"}
    def search_resources(self, query_str: str, limit: int = 100) -> List[Dict[str, Any]]: return []
    def get_relationships(self, resource_id: str) -> List[Dict[str, Any]]: return []
    def get_rules(self, category: str = None) -> List[Dict[str, Any]]: return []
    def query_graph(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        raise NotImplementedError("Graph query not available in mock")
    def get_resource_subgraph(self, resource_id: str) -> Dict[str, Any]:
        return {"resource": self.get_resource(resource_id), "subgraph": {"nodes": [], "edges": []}}

mock_db = MagicMock()
mock_db.query.return_value.all.return_value = []
mock_db.query.return_value.filter.return_value.all.return_value = []
mock_db.query.return_value.filter.return_value.first.return_value = None

def mock_get_db():
    yield mock_db

# Patch dependencies BEFORE app import
import app.database
app.database.SessionLocal = lambda: mock_db
app.database.get_db = mock_get_db

import app.services.graph.neo4j_service as neo4j_module
neo4j_module.Neo4jService = MockNeo4jService

_mock_kc_instance = MockKnowledgeClient()
import knowledge.service.client_factory as kcf_module
kcf_module._default_client = _mock_kc_instance
kcf_module.get_default_client = lambda: _mock_kc_instance

import app.services.graph.analysis.security.security_group_analyzer as sga_mod
import app.services.graph.analysis.security.attack_path_analyzer as apa_mod
import app.services.graph.analysis.security.exposure_analyzer as ea_mod
import app.services.graph.analysis.security.network_analyzer as na_mod
for _mod in [sga_mod, apa_mod, ea_mod, na_mod]:
    _mod.get_default_client = lambda: _mock_kc_instance

try:
    import app.services.graph.analysis.security.iam_analyzer as ia_mod
    ia_mod.get_default_client = lambda: _mock_kc_instance
except ImportError:
    pass

from fastapi.testclient import TestClient
from app.main import app

def _inject_client_into_analyzers(app_instance):
    import sys
    for mod_name in list(sys.modules.keys()):
        mod = sys.modules[mod_name]
        for attr_name in dir(mod):
            try:
                obj = getattr(mod, attr_name)
                if hasattr(obj, "client") and hasattr(obj.client, "get_resource"):
                    obj.client = _mock_kc_instance
            except Exception:
                pass
_inject_client_into_analyzers(app)

# Override dependencies properly in FastAPI
app.dependency_overrides[app.database.get_db] = mock_get_db

client = TestClient(app, raise_server_exceptions=False)

# Collect all endpoints dynamically
endpoints = []
for route in app.routes:
    if isinstance(route, APIRoute):
        methods = list(route.methods - {"OPTIONS"})
        for method in methods:
            # Replace path params e.g. {resource_id} with "mock-id"
            path = re.sub(r"\{.*?\}", "mock-id", route.path)
            endpoints.append((method, path))

# Deduplicate
endpoints = sorted(list(set(endpoints)))

HEADERS = {"Authorization": "Bearer test_user_token"}

results = []

print(f"Testing {len(endpoints)} API endpoints...")

for method, ep in endpoints:
    entry = {"method": method, "endpoint": ep, "status": None}
    try:
        if method == "GET":
            resp = client.get(ep, headers=HEADERS)
        elif method == "POST":
            resp = client.post(ep, headers=HEADERS, json={})
        elif method == "DELETE":
            resp = client.delete(ep, headers=HEADERS)
        elif method == "PUT":
            resp = client.put(ep, headers=HEADERS, json={})
        else:
            continue
            
        entry["status"] = resp.status_code
        if resp.status_code >= 500:
            print(f"❌ HTTP 500: {method} {ep}")
    except Exception as e:
        entry["status"] = 500
        print(f"💥 EXCEPTION {method} {ep}: {e}")

    results.append(entry)

# Summary
passed = [r for r in results if r["status"] and r["status"] < 500]
failed = [r for r in results if r["status"] == 500]

print("\n" + "="*50)
print("FULL API SURFACE TEST SUMMARY")
print("="*50)
print(f"Total endpoints tested: {len(results)}")
print(f"Passed (No 500s):       {len(passed)}")
print(f"Failed (HTTP 500s):     {len(failed)}")

if failed:
    print("\nFAILURES (HTTP 500):")
    for r in failed:
        print(f"- {r['method']} {r['endpoint']}")
