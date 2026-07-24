import urllib.request
import json
import time

tests = [
    "Explain the dependencies of cloudops-db.",
    "What breaks if cloudops-db fails?",
    "Why is cloudops-db insecure?",
    "Show everything related to cloudops-db.",
    "How should I improve this architecture?"
]

for i, test in enumerate(tests, 1):
    print(f"\n========================================")
    print(f"Test {i}: {test}")
    print(f"========================================")
    req = urllib.request.Request(
        "http://localhost:8000/api/v1/ai/chat",
        data=json.dumps({"message": test}).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer demo_user_token"
        },
        method="POST"
    )
    try:
        start = time.time()
        with urllib.request.urlopen(req, timeout=120) as res:
            body = res.read().decode("utf-8")
            try:
                data = json.loads(body)
                print(data.get("answer", body))
            except:
                print(body)
        print(f"\n[Time taken: {time.time() - start:.1f}s]")
    except Exception as e:
        print(f"Error: {e}")
