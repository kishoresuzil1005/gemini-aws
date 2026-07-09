import re

with open("backend/app/services/discovery/scanner.py", "r") as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    # Identify the start of a provider block
    if "for " in line and "in " in line and "Discovery.discover(" in line:
        # e.g. "for inst in EC2Discovery.discover(reg):"
        match = re.search(r'for \w+ in (\w+Discovery\.discover\(.*?\)):', line)
        if match:
            new_lines.append(f"                resources.extend({match.group(1)})\n")
            skip = True
            continue
            
    if skip:
        if line.strip() == "" or line.strip() == "except Exception as e:":
            skip = False
            new_lines.append(line)
        continue
        
    new_lines.append(line)

with open("backend/app/services/discovery/scanner.py", "w") as f:
    f.writelines(new_lines)
