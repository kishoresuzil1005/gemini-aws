import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from fastapi.testclient import TestClient
from app.main import app
from app.bootstrap import BootstrapManager


def test_startup():
    with TestClient(app) as client:
        # Check health endpoint
        response = client.get("/api/v1/platform/health")
        assert response.status_code == 200, f"Health endpoint failed: {response.text}"
        data = response.json()
        assert data["status"] == "HEALTHY", f"Platform is not healthy: {data}"
        
        # Check readiness endpoint
        response = client.get("/api/v1/platform/readiness")
        assert response.status_code == 200, f"Readiness endpoint failed: {response.text}"
        data = response.json()
        assert data["ready"] is True, f"Platform is not ready: {data}"
        print("Integration Test Passed!")

if __name__ == "__main__":
    test_startup()
