import os

fixes = [
    (
        'backend/app/services/graph/core/graph_snapshot.py',
        'import json\n',
        'import json\nfrom typing import Any\n'
    ),
    (
        'backend/app/services/graph/helpers/graph_metadata_helper.py',
        'from typing import List, Any\n',
        'from typing import List, Any, Dict\n'
    ),
    (
        'backend/app/services/ai/assistant/self_healing/planning/strategies/canary_strategy.py',
        'from ....models.healing_models import RepairPlan',
        'from ...models.healing_models import RepairPlan'
    ),
    (
        'backend/app/services/optimization/recommendations.py',
        'RecommendationsEngine = RecommendationEngin',
        'RecommendationsEngine = RecommendationEngine'
    ),
    (
        'backend/app/services/ai/assistant/learning/utils/learning_serializer.py',
        'pas\n',
        'pass\n'
    ),
    (
        'backend/app/services/ai/assistant/learning/utils/learning_exporter.py',
        'pas\n',
        'pass\n'
    ),
    (
        'backend/app/services/ai/assistant/learning/analytics/trend_engine.py',
        'pas\n',
        'pass\n'
    ),
    (
        'backend/app/services/ai/assistant/learning/analytics/anomaly_engine.py',
        'pas\n',
        'pass\n'
    ),
    (
        'backend/app/services/ai/assistant/learning/analytics/pattern_engine.py',
        'pas\n',
        'pass\n'
    )
]

for path, old, new in fixes:
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        if old in content:
            content = content.replace(old, new)
            with open(path, 'w') as f:
                f.write(content)
            print(f"Fixed {path}")
        else:
            print(f"Warning: Could not find '{old}' in {path}")
    else:
        print(f"Warning: File not found {path}")
