import sys
import os
sys.path.insert(0, os.path.abspath('backend'))
from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("--- METADATA ---")
res = db.execute(text("SELECT resource_type, metadata FROM resources LIMIT 5")).fetchall()
for r in res:
    print(r)

print("\n--- SCAN HISTORY ---")
res = db.execute(text("SELECT id, status, resources_found, errors, warnings FROM scan_history")).fetchall()
for r in res:
    print(r)

print("\n--- RELATIONSHIPS ---")
res = db.execute(text("SELECT source_resource_id, target_resource_id, relationship_type FROM resource_relationships LIMIT 5")).fetchall()
for r in res:
    print(r)

print("\n--- SCAN IDs ---")
res = db.execute(text("SELECT resource_type, scan_id FROM resources LIMIT 5")).fetchall()
for r in res:
    print(r)

print("\n--- VERSIONS ---")
res = db.execute(text("SELECT resource_type, resource_version FROM resources LIMIT 5")).fetchall()
for r in res:
    print(r)

db.close()
