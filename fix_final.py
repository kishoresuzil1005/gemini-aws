import os
import re

# Fix FailureAnalysis
for fpath in [
    'backend/app/main.py', 
    'backend/app/api/topology.py', 
    'backend/app/services/topology/topology_service.py', 
    'backend/app/services/ai/architecture_service.py'
]:
    if os.path.exists(fpath):
        with open(fpath, 'r') as f:
            c = f.read()
        c = c.replace('import FailureAnalysis', 'import FailureAnalysisService as FailureAnalysis')
        with open(fpath, 'w') as f:
            f.write(c)

# Fix ProductionChecklist
path = 'backend/app/services/ai/production_best_practices.py'
if os.path.exists(path):
    with open(path, 'r') as f:
        c = f.read()
    c = c.replace('import ProductionChecklist', 'import ProductionChecklistService as ProductionChecklist')
    with open(path, 'w') as f:
        f.write(c)

# Fix GenericResourceType
path = 'backend/app/providers/common/models.py'
if os.path.exists(path):
    with open(path, 'r') as f:
        c = f.read()
    if 'KUBERNETES' not in c:
        c = c.replace('class GenericResourceType(str, Enum):', "class GenericResourceType(str, Enum):\n    KUBERNETES = 'kubernetes'\n    SECURITY = 'security'")
    with open(path, 'w') as f:
        f.write(c)

# Fix Any
path = 'backend/app/services/ai/assistant/knowledge_graph/intelligence/topology_engine.py'
if os.path.exists(path):
    with open(path, 'r') as f:
        c = f.read()
    if 'Any' not in c and 'from typing import' in c:
        c = re.sub(r'from typing import (.+)', r'from typing import \1, Any', c, count=1)
    with open(path, 'w') as f:
        f.write(c)

# Add celery
req = 'backend/requirements.txt'
with open(req, 'a') as f:
    f.write('\ncelery>=5.3.6\n')

# Create missing graph_context.py
with open('backend/app/services/ai/graph_context.py', 'w') as f:
    f.write('''
class GraphContextBuilder:
    def get_context(self, resource_id: str):
        return {"resource": resource_id, "dependencies": []}
''')

# Create missing insights.py
with open('backend/app/services/ai/insights.py', 'w') as f:
    f.write('''
class AIInsightsService:
    def generate_insights(self, query: str):
        return {"insights": []}
''')

