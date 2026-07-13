import ast, os, sys
from itertools import product

def repair_file(path):
    with open(path, 'r') as f:
        content = f.read()
    
    try:
        ast.parse(content)
        return True
    except SyntaxError:
        pass
        
    brackets = [')', ']', '}']
    suffixes = ['']
    for length in range(1, 6):
        for p in product(brackets, repeat=length):
            suffixes.append(''.join(p))
            
    # Include strings
    extended_suffixes = []
    for s in suffixes:
        extended_suffixes.append(s)
        extended_suffixes.append('"' + s)
        extended_suffixes.append("'" + s)
        extended_suffixes.append('""' + s)
        extended_suffixes.append("''" + s)
        
    for suf in extended_suffixes:
        for pre in ['', '\n', ' ', '\n    ', '\n        ']:
            test_content = content + pre + suf
            try:
                ast.parse(test_content)
                with open(path, 'w') as f:
                    f.write(test_content)
                print(f"Fixed {path} with pre={repr(pre)}, suf={repr(suf)}")
                return True
            except SyntaxError:
                pass
                
    print(f"Failed to fix {path}")
    return False

errors = []
for root, _, files in os.walk('backend/app'):
    for f in files:
        if not f.endswith('.py'): continue
        path = os.path.join(root, f)
        try:
            with open(path) as fp: src = fp.read()
            ast.parse(src)
        except SyntaxError:
            errors.append(path)

for path in errors:
    repair_file(path)

