import os

fixes = [
    'backend/app/services/ai/assistant/learning/analytics/pattern_engine.py',
    'backend/app/services/ai/assistant/learning/analytics/anomaly_engine.py',
    'backend/app/services/ai/assistant/learning/analytics/trend_engine.py',
    'backend/app/services/ai/assistant/learning/utils/learning_exporter.py',
    'backend/app/services/ai/assistant/learning/utils/learning_serializer.py'
]

for path in fixes:
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        if 'pas' in content:
            # specifically replace exactly '    pas' with '    pass' at the end of the file or globally
            content = content.replace('    pas', '    pass')
            with open(path, 'w') as f:
                f.write(content)
            print(f"Fixed {path}")
