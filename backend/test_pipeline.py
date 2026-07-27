import sys
import os

# Add the backend directory to sys.path so we can import app modules
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.services.ai.assistant.graph_assistant import GraphAssistant
from app.services.ai.assistant.assistant_models import ChatRequest

def run_test():
    assistant = GraphAssistant()
    
    queries = [
        "Analyze EC2 i-0123456789abcdef0",
        "Analyze web-server",
        "Analyze production VPC",
        "Analyze EC2",
        "Analyze server xyz123"
    ]
    
    for i, q in enumerate(queries):
        req = ChatRequest(
            conversation_id=f"test-p2-{i}",
            message=q
        )
        print(f"\n--- E2E TEST: {q} ---")
        response = assistant.chat(req)
        print("Status:", response.status)
        print("Answer:", response.answer)

    print("\n--- E2E TEST: Memory (Analyze web-server -> Restart it) ---")
    req1 = ChatRequest(conversation_id="test-memory", message="Analyze web-server")
    response1 = assistant.chat(req1)
    print("Q1 Status:", response1.status)
    req2 = ChatRequest(conversation_id="test-memory", message="Restart it")
    response2 = assistant.chat(req2)
    print("Q2 Status:", response2.status)
    print("Q2 Answer:", response2.answer)
    
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    run_test()
