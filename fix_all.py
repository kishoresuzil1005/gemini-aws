import os

for root, _, files in os.walk('backend/app'):
    for f in files:
        if not f.endswith('.py'): continue
        path = os.path.join(root, f)
        
        with open(path, 'r') as fp:
            content = fp.read()
            
        original_content = content
        
        # fix 'pas' at end of file or line
        if 'pas\n' in content:
            content = content.replace('    pas\n', '    pass\n')
            content = content.replace('        pas\n', '        pass\n')
        if content.endswith('pas'):
            content = content[:-3] + 'pass'
            
        # fix 'floa' at end of file or line
        if 'floa\n' in content:
            content = content.replace('floa\n', 'float\n')
        if content.endswith('floa'):
            content = content[:-4] + 'float'
            
        # fix 'mission_i' at end of file or line
        if 'mission_i\n' in content:
            content = content.replace('mission_i\n', 'mission_id\n')
        if content.endswith('mission_i'):
            content = content[:-9] + 'mission_id'
            
        # fix 'decorato' at end of file or line
        if 'decorato\n' in content:
            content = content.replace('decorato\n', 'decorator\n')
        if content.endswith('decorato'):
            content = content[:-8] + 'decorator'
            
        if path.endswith('mission_manager.py'):
            content = content.replace('from typing import Dict, List, Optional', 'from typing import Dict, List, Optional, Any')
            
        if content != original_content:
            with open(path, 'w') as fp:
                fp.write(content)
            print(f"Fixed {path}")
