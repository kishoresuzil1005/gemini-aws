import sys
import json
from app.main import app
from fastapi.routing import APIRoute

routes = []
for route in app.routes:
    if isinstance(route, APIRoute):
        methods = ",".join(route.methods)
        routes.append(f"{methods} {route.path}")

# Deduplicate in case of multiple methods, though usually they are separate or combined
unique_routes = sorted(list(set(routes)))

with open("all_apis.md", "w") as f:
    f.write(f"# Complete Backend API List ({len(unique_routes)} Endpoints)\n\n")
    for r in unique_routes:
        f.write(f"- `{r}`\n")

print(f"Extracted {len(unique_routes)} endpoints.")
