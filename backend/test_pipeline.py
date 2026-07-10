import sys
import os

# Add the backend directory to sys.path so we can import app modules
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.services.ai.assistant.graph_assistant import GraphAssistant
from app.services.ai.assistant.assistant_models import ChatRequest

def run_test():
    assistant = GraphAssistant()
    
    # 1. Test basic inventory query
    req = ChatRequest(
        conversation_id="test-123",
        message="Analyze EC2 i-027d09b80036bb765"
    )
    print("\n--- E2E TEST: Analysis ---")
    response = assistant.chat(req)
    print("Status:", response.status)
    print("Answer:", response.answer)
    
if __name__ == "__main__":
    run_test()
