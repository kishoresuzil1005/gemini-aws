import sys
from fastapi.testclient import TestClient
from app.main import app
import traceback

client = TestClient(app, raise_server_exceptions=True)

print("Testing FinOps recommendations...")
try:
    response = client.get("/api/v1/finops/recommendations", headers={"Authorization": "Bearer test_user_token"})
    print(response.status_code)
except Exception as e:
    print("Caught Exception!")
    traceback.print_exc()
