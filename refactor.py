import os
import glob
import re

base_keys = {"resource_id", "resource_type", "region", "name", "status"}

def parse_dict(dict_str):
    # This is a bit hacky, let's find a safer way.
    pass

# We can also just read the files and rewrite the dictionary logic
# using a python script that actually imports the module, gets the ast, and rewrites it.
import ast

class RewriteAppend(ast.NodeTransformer):
    def __init__(self, filename):
        self.filename = filename

    def visit_Call(self, node):
        self.generic_visit(node)
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'append':
            if len(node.args) == 1 and isinstance(node.args[0], ast.Dict):
                d = node.args[0]
                keys = []
                values = []
                meta_keys = []
                meta_values = []
                
                has_provider = False
                has_resource_type = False
                has_resource_id = False
                has_name = False
                has_region = False
                has_status = False
                
                for k, v in zip(d.keys, d.values):
                    if isinstance(k, ast.Constant):
                        key_name = k.value
                        if key_name == "provider":
                            has_provider = True
                            keys.append(k)
                            values.append(v)
                        elif key_name == "resource_id":
                            has_resource_id = True
                            keys.append(k)
                            values.append(v)
                        elif key_name == "resource_type":
                            has_resource_type = True
                            keys.append(k)
                            values.append(v)
                        elif key_name == "name":
                            has_name = True
                            keys.append(k)
                            values.append(v)
                        elif key_name == "region":
                            has_region = True
                            keys.append(k)
                            values.append(v)
                        elif key_name == "status":
                            has_status = True
                            keys.append(k)
                            values.append(v)
                        elif key_name == "state" and not has_status:
                            has_status = True
                            keys.append(ast.Constant("status"))
                            values.append(v)
                        elif key_name in ("metadata", "dependencies"):
                            pass # skip if already processed
                        else:
                            meta_keys.append(k)
                            meta_values.append(v)
                
                # Default additions
                if not has_provider:
                    keys.append(ast.Constant("provider"))
                    values.append(ast.Constant("AWS"))
                
                # Check for 'state' in meta_keys to remove if it was renamed to status
                # But we handled it above.
                
                # Dependencies handling logic based on file
                deps = ast.List(elts=[], ctx=ast.Load())
                if "subnet.py" in self.filename:
                    # add vpc
                    pass # We will do dependencies manually for the few files that need it, or build logic here.
                    
                keys.append(ast.Constant("metadata"))
                values.append(ast.Dict(keys=meta_keys, values=meta_values))
                
                # For now, just empty deps, we can add them manually or via script for the few that have it
                keys.append(ast.Constant("dependencies"))
                values.append(deps)
                
                node.args[0] = ast.Dict(keys=keys, values=values)
        return node

for f in glob.glob("backend/app/providers/aws/*.py"):
    if os.path.basename(f) in ["__init__.py", "auth.py", "regions.py", "ce.py", "cloudwatch.py", "cost_explorer.py", "inventory.py"]:
        continue
        
    with open(f, "r") as file:
        src = file.read()
    
    if "resources.append" not in src and "append({" not in src:
        continue
        
    try:
        tree = ast.parse(src)
        transformer = RewriteAppend(f)
        new_tree = transformer.visit(tree)
        ast.fix_missing_locations(new_tree)
        new_src = ast.unparse(new_tree)
        with open(f, "w") as file:
            file.write(new_src)
        print(f"Rewrote {f}")
    except Exception as e:
        print(f"Failed {f}: {e}")

