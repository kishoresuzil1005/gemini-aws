import os
import sys
import json
from pathlib import Path

# Fix python search path to import backend modules correctly
RUNNING_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = RUNNING_DIR
for _ in range(5):
    if (PROJECT_ROOT / "app").exists():
        break
    PROJECT_ROOT = PROJECT_ROOT.parent

sys.path.insert(0, str(PROJECT_ROOT))

from app.services.ai.qdrant_service import QdrantService

unresolved_paths = [
    "backend/data/aws_docs",
    "data/aws_docs"
]

DATA_DIR = None
for path in unresolved_paths:
    p = RUNNING_DIR
    found = False
    for i in range(5):
        test_path = p / path
        if test_path.exists():
            DATA_DIR = test_path
            found = True
            break
        p = p.parent
    if found:
        break

if not DATA_DIR:
    DATA_DIR = Path("/backend/data/aws_docs")

EMBEDDED_DIR = DATA_DIR / "embedded"

def run_load_qdrant():
    print(f"[LOAD QDRANT] Locating embedded points profiles from: {EMBEDDED_DIR}")
    
    if not EMBEDDED_DIR.exists():
        print(f"[LOAD QDRANT] Error: EMBEDDED_DIR {EMBEDDED_DIR} does not exist!")
        return
        
    embedded_files = list(EMBEDDED_DIR.glob("*_embedded.json"))
    if not embedded_files:
        print("[LOAD QDRANT] No embedded JSON vector logs found. Run embedder.py first.")
        return
        
    print("[LOAD QDRANT] Connecting to core Qdrant Service...")
    qs = QdrantService(collection_name="cloud_docs")
    
    all_points = []
    for emb_f in embedded_files:
        print(f"[LOAD QDRANT] Reading {emb_f.name}...")
        with open(emb_f, "r", encoding="utf-8") as f:
            points = json.load(f)
            all_points.extend(points)
            
    if not all_points:
        print("[LOAD QDRANT] No points loaded to upsert.")
        return
        
    print(f"[LOAD QDRANT] Initiating upsert of {len(all_points)} vectors to Qdrant...")
    result = qs.upsert_vectors(all_points)
    
    if result:
        print(f"[LOAD QDRANT] Successfully upserted {len(all_points)} vector points to 'cloud_docs' collection!")
    else:
        print("[LOAD QDRANT] Warning: Qdrant upsert returned failure.")

if __name__ == "__main__":
    run_load_qdrant()
