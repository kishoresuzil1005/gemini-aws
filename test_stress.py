import sys
import os
import threading
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from fastapi.testclient import TestClient
from app.main import app

def run_stress_test(concurrency: int):
    print(f"Running stress test with {concurrency} concurrent requests...")
    results = []
    
    def task():
        try:
            with TestClient(app) as client:
                res_health = client.get("/api/v1/platform/health")
                res_metrics = client.get("/api/v1/platform/metrics")
                res_test = client.get("/api/v1/platform/self-test")
                
                if res_health.status_code == 200 and res_metrics.status_code == 200 and res_test.status_code == 200:
                    results.append(True)
                else:
                    results.append(False)
        except Exception as e:
            results.append(False)
            
    threads = [threading.Thread(target=task) for _ in range(concurrency)]
    for t in threads: t.start()
    for t in threads: t.join()
    
    successes = sum(results)
    print(f"Successes: {successes}/{concurrency}")
    return successes == concurrency

if __name__ == "__main__":
    assert run_stress_test(10)
    assert run_stress_test(100)
    print("Stress tests passed!")
