import os
import re

def clean_file(fpath):
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace "raise NotImplementedError" with "..."
    # Match raise NotImplementedError and optionally parenthesis and string
    new_content = re.sub(r'raise\s+NotImplementedError(\([^)]*\))?', '...', content)

    # Replace pass with ...
    new_content = re.sub(r'\bpass\b', '...', new_content)

    if new_content != content:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Cleaned {fpath}")

def clean_all():
    for root, dirs, files in os.walk('knowledge'):
        for f in files:
            if f.endswith('.py'):
                clean_file(os.path.join(root, f))

if __name__ == '__main__':
    clean_all()
