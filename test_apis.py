import urllib.request
import json
import time

BASE_URL = "http://54.205.123.215:8000"

def main():
    print("Starting API test script...")
    with open("api.txt", "w") as f:
        f.write("=== API Test Results ===\n\n")

    # 1. Register
    register_payload = {
        "email": f"testuser_{int(time.time())}@example.com",
        "password": "Password123!",
        "organizationName": "Test Org",
        "plan": "BASIC",
        "role": "ORG_ADMIN"
    }
    
    data = json.dumps(register_payload).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/v1/auth/register", data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            res_body = response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        status_code = e.code
        res_body = e.read().decode('utf-8')
    except Exception as e:
        print(f"Registration failed: {e}")
        return

    with open("api.txt", "a") as f:
        f.write(f"--- POST /api/v1/auth/register ---\n")
        f.write(f"Status: {status_code}\n")
        f.write(f"Response: {res_body}\n\n")
        
    if status_code not in [200, 201]:
        print("Registration failed. Exiting.")
        return
        
    res_json = json.loads(res_body)
    token = res_json.get("accessToken")
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    
    # List of endpoints to test
    endpoints = [
        "/api/v1/auth/me",
        "/api/v1/accounts",
        "/api/v1/inventory",
        "/api/v1/inventory/resources",
        "/api/v1/inventory/resources/compute",
        "/api/v1/inventory/resources/databases",
        "/api/v1/inventory/resources/summary",
        "/api/v1/inventory/scan/history",
        "/api/v1/topology",
        "/api/v1/graph/health",
        "/api/v1/graph/stats",
        "/api/v1/cost/summary",
        "/api/v1/billing/summary",
        "/api/v1/ec2/instances",
        "/health",
        "/ready",
        "/live"
    ]
    
    for endpoint in endpoints:
        print(f"Testing {endpoint}...")
        try:
            req = urllib.request.Request(f"{BASE_URL}{endpoint}", headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                status_code = response.getcode()
                res_body = response.read().decode('utf-8')
                
            with open("api.txt", "a") as f:
                f.write(f"--- GET {endpoint} ---\n")
                f.write(f"Status: {status_code}\n")
                f.write(f"Response: {res_body[:1000]}\n\n")
        except urllib.error.HTTPError as e:
            with open("api.txt", "a") as f:
                f.write(f"--- GET {endpoint} ---\n")
                f.write(f"Status: {e.code}\n")
                f.write(f"Response: {e.read().decode('utf-8')[:1000]}\n\n")
        except Exception as e:
            with open("api.txt", "a") as f:
                f.write(f"--- GET {endpoint} ---\n")
                f.write(f"Error: {str(e)}\n\n")
                
    print("Testing complete. Results saved to api.txt")

if __name__ == "__main__":
    main()
