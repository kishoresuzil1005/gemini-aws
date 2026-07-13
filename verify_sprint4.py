import sys
from backend.app.services.graph.sync.graph_sync_engine import GraphSyncEngine

class MockEventPublisher:
    def publish(self, event_type, payload):
        print(f"[MOCK BUS] Published {event_type} with payload: {payload}")

class MockNeo4jClient:
    pass

def test_sync_pipeline():
    print("Testing Graph Sync Pipeline...")
    neo4j = MockNeo4jClient()
    bus = MockEventPublisher()
    
    engine = GraphSyncEngine(neo4j, bus)
    
    node_diffs = {
        "added": [{"id": "i-123"}],
        "changed": [],
        "removed": []
    }
    
    edge_diffs = {
        "added_edges": [{"source": "i-123", "target": "vpc-1"}],
        "changed_edges": [],
        "removed_edges": []
    }
    
    engine.run_sync_pipeline("aws", node_diffs, edge_diffs)

if __name__ == "__main__":
    test_sync_pipeline()
