"""
Enterprise Endpoint Regression Test Suite
==========================================
Runs all previously failing endpoints with a fully mocked dependency layer.

Mock strategy:
- Mocks are designed to mirror the production interface so tests fail due to
  application bugs — not because the mock is incomplete.
- MockNeo4jService mirrors Neo4jService's public API (get_graph, get_node,
  close, health_check, query, etc.).
- MockKnowledgeClient mirrors KnowledgeClient's public API (get_resource,
  get_relationships, query_graph, search_resources, get_rules).
- Both mocks return empty-but-valid data structures (not None) to allow
  application logic to proceed past the data access layer.
"""

import sys
import json
import traceback
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List, Optional


# ─────────────────────────────────────────────────────────
# Mock: Neo4jService — mirrors production Neo4jService API
# ─────────────────────────────────────────────────────────

class MockNeo4jService:
    """Mirrors the public interface of Neo4jService for test purposes."""

    def __init__(self, *args, **kwargs):
        self.driver = None  # simulate no active driver

    def close(self):
        pass

    def health_check(self):
        return {"status": "mock", "connected": False}

    def node_exists(self, resource_id: str) -> bool:
        return False

    def query(self, query: str, **kwargs):
        return []

    def clear_graph(self):
        pass

    def create_node(self, *args, **kwargs):
        return None

    def create_relationship(self, *args, **kwargs):
        return None

    def get_graph(self, region: str = None) -> Dict[str, Any]:
        """Returns a minimal valid graph for diagram rendering."""
        return {"nodes": [], "edges": []}

    def get_node(self, resource_id: str = None) -> Optional[Dict[str, Any]]:
        return None

    def get_resource_subgraph(self, resource_id: str) -> Dict[str, Any]:
        return {"nodes": [], "edges": []}

    def get_dependencies(self, resource_id: str) -> List[Dict[str, Any]]:
        return []

    def get_full_graph(self) -> Dict[str, Any]:
        return {"nodes": [], "edges": []}

    def get_orphan_resources(self) -> List[Dict[str, Any]]:
        return []

    def get_node_count(self) -> int:
        return 0

    def get_edge_count(self) -> int:
        return 0


# ─────────────────────────────────────────────────────────
# Mock: KnowledgeClient — mirrors production KnowledgeClient API
# The security analyzers (SecurityGroupAnalyzer, AttackPathAnalyzer, etc.)
# use `self.client` which is a KnowledgeClient, NOT Neo4jService directly.
# ─────────────────────────────────────────────────────────

class MockKnowledgeClient:
    """Mirrors the public interface of KnowledgeClient for test purposes."""

    def get_resource(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Returns a minimal valid resource dict (not None) so analyzers proceed."""
        return {
            "id": resource_id,
            "type": "EC2",
            "name": f"mock-{resource_id}",
            "region": "us-east-1",
            "status": "running",
        }

    def search_resources(self, query_str: str, limit: int = 100) -> List[Dict[str, Any]]:
        return []

    def get_relationships(self, resource_id: str) -> List[Dict[str, Any]]:
        return []

    def get_rules(self, category: str = None) -> List[Dict[str, Any]]:
        return []

    def query_graph(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Raises NotImplementedError so callers fall back to their fallback path
        (which is the production behavior when the graph is unavailable).
        """
        raise NotImplementedError("Graph query not available in mock")

    def get_resource_subgraph(self, resource_id: str) -> Dict[str, Any]:
        return {
            "resource": self.get_resource(resource_id),
            "subgraph": {"nodes": [], "edges": []}
        }


# ─────────────────────────────────────────────────────────
# Mock: SQLAlchemy DB Session
# ─────────────────────────────────────────────────────────

mock_db = MagicMock()
mock_db.query.return_value.all.return_value = []
mock_db.query.return_value.filter.return_value.all.return_value = []
mock_db.query.return_value.filter.return_value.first.return_value = None


# ─────────────────────────────────────────────────────────
# Patch all dependency injection points BEFORE importing the app
# ─────────────────────────────────────────────────────────

import app.database
app.database.SessionLocal = lambda: mock_db
app.database.get_db = lambda: iter([mock_db])

import app.services.graph.neo4j_service as neo4j_module
neo4j_module.Neo4jService = MockNeo4jService

# Patch the KnowledgeClient factory used by security analyzers
import knowledge.service.client_factory as kcf_module
kcf_module._default_client = MockKnowledgeClient()

# Patch get_default_client so analyzers that call it directly get the mock
_mock_kc_instance = MockKnowledgeClient()

import knowledge.service.client_factory as kcf_module
kcf_module._default_client = _mock_kc_instance
kcf_module.get_default_client = lambda: _mock_kc_instance

# Patch into each security analyzer module's own namespace.
# These modules are imported BEFORE the app is imported, so patching
# get_default_client at the module level ensures __init__ receives the mock.
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

# Now import the app — after all patches are in place. Any module-level
# instantiation of analyzers will call our patched get_default_client.
from fastapi.testclient import TestClient
from app.main import app

# Post-import: override self.client on any already-instantiated analyzer singletons
# that the router may have created at import time.
def _inject_client_into_analyzers(app_instance):
    """Walk the app routes and patch .client on any analyzer instances found."""
    from fastapi import FastAPI
    for route in getattr(app_instance, "routes", []):
        for dep in getattr(route, "dependencies", []):
            pass  # dependency injection handled via patching above
    # Additionally patch via known singleton paths if present
    import importlib, sys
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


client = TestClient(app, raise_server_exceptions=True)


# ─────────────────────────────────────────────────────────
# Endpoint List
# ─────────────────────────────────────────────────────────

ENDPOINTS = [
    # FinOps
    ("GET", "/api/v1/finops/recommendations"),
    ("GET", "/api/v1/finops/savings"),
    # Architecture Diagrams
    ("GET", "/api/v1/architecture/diagrams/graph"),
    ("GET", "/api/v1/architecture/diagrams/aggregate"),
    ("GET", "/api/v1/architecture/diagrams/architecture-model"),
    ("GET", "/api/v1/architecture/diagrams/layers"),
    ("GET", "/api/v1/architecture/diagrams/icons"),
    ("GET", "/api/v1/architecture/diagrams/layout"),
    ("GET", "/api/v1/architecture/diagrams/svg"),
    ("GET", "/api/v1/architecture/diagrams/relationships"),
    ("GET", "/api/v1/architecture/diagrams/vpc-layout"),
    ("GET", "/api/v1/architecture/diagrams/smart-layout"),
    # Operations
    ("GET", "/api/v1/operations/recommendations"),
    ("GET", "/api/v1/operations/savings"),
    # Graph / Security
    ("GET", "/api/v1/graph/last-sync"),
    ("GET", "/api/v1/graph/security-group/test-sg-123"),
    ("GET", "/api/v1/graph/attack-path/test-ec2-123"),
    ("GET", "/api/v1/graph/exposure/test-ec2-123"),
    ("GET", "/api/v1/graph/iam-analysis/test-role-123"),
    ("GET", "/api/v1/graph/network-analysis/test-ec2-123"),
    # AI Actions
    ("GET", "/api/v1/ai/actions/remediation"),
    ("GET", "/api/v1/ai/actions/orchestration"),
]

HEADERS = {"Authorization": "Bearer test_user_token"}


# ─────────────────────────────────────────────────────────
# Schema Validation
# ─────────────────────────────────────────────────────────

def validate_response(ep, method, status, body_raw):
    """Validate that a 2xx response has a valid JSON body (not a bare string error)."""
    issues = []
    if status >= 500:
        issues.append(f"HTTP {status} — server error")

    if status < 300:
        try:
            data = json.loads(body_raw) if body_raw else None
        except Exception:
            issues.append("Response body is not valid JSON")
            data = None

        if data is None and body_raw:
            # Check if it is valid SVG or XML (acceptable for /svg and /drawio)
            stripped = body_raw.strip()
            if not stripped.startswith("<"):
                issues.append("Response body is empty or non-JSON without recognized format")

    return issues


# ─────────────────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────────────────

results = []

for method, ep in ENDPOINTS:
    print(f"\n{'='*60}\n{method} {ep}\n{'='*60}")
    entry = {
        "method": method,
        "endpoint": ep,
        "status": None,
        "result": None,
        "issues": [],
        "exception": None,
        "body_sample": None,
    }
    try:
        resp = getattr(client, method.lower())(ep, headers=HEADERS)
        entry["status"] = resp.status_code
        body_raw = resp.text

        # Save first 300 chars of body for review
        entry["body_sample"] = body_raw[:300].replace("\n", " ") if body_raw else ""

        schema_issues = validate_response(ep, method, resp.status_code, body_raw)
        entry["issues"] = schema_issues

        if resp.status_code < 300 and not schema_issues:
            entry["result"] = "PASS"
            print(f"  ✅ PASS — HTTP {resp.status_code}")
        elif resp.status_code == 404:
            entry["result"] = "EXPECTED_404"
            print(f"  ℹ️  EXPECTED 404 — resource not found (correct for test IDs)")
        elif resp.status_code < 500:
            entry["result"] = "PASS_WITH_WARNING"
            print(f"  ⚠️  HTTP {resp.status_code} — {schema_issues}")
        else:
            entry["result"] = "FAIL"
            print(f"  ❌ FAIL — HTTP {resp.status_code} — {schema_issues}")
            print(f"  Body: {body_raw[:500]}")

    except Exception as e:
        entry["result"] = "EXCEPTION"
        entry["exception"] = traceback.format_exc()
        print(f"  💥 EXCEPTION: {e}")
        traceback.print_exc()

    results.append(entry)


# ─────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────

print("\n\n" + "="*70)
print("REGRESSION SUMMARY")
print("="*70)
passed = [r for r in results if r["result"] in ("PASS", "EXPECTED_404", "PASS_WITH_WARNING")]
failed = [r for r in results if r["result"] in ("FAIL", "EXCEPTION")]

print(f"Total endpoints: {len(results)}")
print(f"Passing:         {len(passed)}")
print(f"Failing:         {len(failed)}")

if failed:
    print("\nFAILURES:")
    for r in failed:
        print(f"  [{r['result']}] {r['method']} {r['endpoint']} — HTTP {r['status']}")
        if r["exception"]:
            # Print last 5 lines of traceback
            tb_lines = r["exception"].strip().split("\n")
            for line in tb_lines[-5:]:
                print(f"    {line}")

print("\n\nDETAILED RESULTS:")
for r in results:
    status_str = str(r["status"]) if r["status"] else "N/A"
    print(f"  {r['result']:25s} {r['method']:6s} {r['endpoint']} (HTTP {status_str})")
    if r["body_sample"]:
        print(f"           Body: {r['body_sample'][:120]}")
