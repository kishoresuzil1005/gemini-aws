import os

TESTS_DIR = "tests/providers/common"
os.makedirs(TESTS_DIR, exist_ok=True)

test_content = """import pytest
from backend.app.providers.common.inventory_diff import InventoryDiffEngine

def test_inventory_diff_added_removed_changed():
    engine = InventoryDiffEngine()
    
    old_inventory = [
        {"resource_id": "i-123", "status": "running"},
        {"resource_id": "i-456", "status": "stopped"}
    ]
    
    new_inventory = [
        {"resource_id": "i-123", "status": "stopped"}, # Changed
        {"resource_id": "i-789", "status": "running"}  # Added
        # i-456 Removed
    ]
    
    diff = engine.calculate_diff(old_inventory, new_inventory)
    
    assert len(diff["added"]) == 1
    assert diff["added"][0]["resource_id"] == "i-789"
    
    assert len(diff["changed"]) == 1
    assert diff["changed"][0]["resource_id"] == "i-123"
    assert diff["changed"][0]["status"] == "stopped"
    
    assert len(diff["removed"]) == 1
    assert diff["removed"][0]["resource_id"] == "i-456"

def test_inventory_diff_no_changes():
    engine = InventoryDiffEngine()
    
    inventory = [
        {"resource_id": "i-123", "status": "running"}
    ]
    
    diff = engine.calculate_diff(inventory, inventory)
    
    assert len(diff["added"]) == 0
    assert len(diff["changed"]) == 0
    assert len(diff["removed"]) == 0
"""

filepath = os.path.join(TESTS_DIR, "test_inventory_diff.py")
with open(filepath, "w") as f:
    f.write(test_content)
    
print(f"Created {filepath}")
