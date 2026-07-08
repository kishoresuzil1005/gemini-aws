import re

with open("backend/app/services/discovery/scanner.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    match = re.search(r'resources.extend\((\w+)Discovery\.discover', line)
    if match:
        provider = match.group(1)
        indent = line[:line.find('resources')]
        new_lines.append(f'{indent}print("{provider.upper()} START")\n')
        new_lines.append(line)
        new_lines.append(f'{indent}print("{provider.upper()} DONE")\n')
    else:
        new_lines.append(line)

with open("backend/app/services/discovery/scanner.py", "w") as f:
    f.writelines(new_lines)
