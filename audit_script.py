import os
import re
import ast

def audit():
    knowledge_dir = "knowledge"
    
    # Phase 2: Package Verification
    packages = []
    missing_init = []
    
    for root, dirs, files in os.walk(knowledge_dir):
        if "__init__.py" not in files:
            missing_init.append(root)
        else:
            packages.append(root)
            
    # Phase 3: Public API Verification
    not_implemented_methods = []
    todo_apis = []
    
    # Phase 6: Hardcoded Knowledge
    hardcoded = []
    
    # Phase 8: Code Quality
    code_quality_issues = []
    
    keywords_p8 = re.compile(r'\b(TODO|FIXME|XXX|HACK|pass|NotImplementedError|deprecated|placeholder|experimental|mock)\b', re.IGNORECASE)
    
    # Phase 4: Dependency Verification (simple string check)
    circular_imports = []
    leaks = []
    
    # Phase 1: Architecture
    subsystems = {
        "Knowledge Models": False,
        "Provider Framework": False,
        "Source Connectors": False,
        "Validation Engine": False,
        "Parser Engine": False,
        "Extractor Engine": False,
        "Normalization Engine": False,
        "Resource Catalog": False,
        "Relationship Catalog": False,
        "Rule Catalog": False,
        "Knowledge Graph": False,
        "Knowledge Service": False,
        "Snapshot Manager": False,
        "Search Engine": False,
        "Analyzer Integration Layer": False,
    }
    
    if os.path.exists(os.path.join(knowledge_dir, "models")): subsystems["Knowledge Models"] = True
    if os.path.exists(os.path.join(knowledge_dir, "providers")): subsystems["Provider Framework"] = True
    if os.path.exists(os.path.join(knowledge_dir, "providers", "aws", "connectors")): subsystems["Source Connectors"] = True
    if os.path.exists(os.path.join(knowledge_dir, "validation")): subsystems["Validation Engine"] = True
    if os.path.exists(os.path.join(knowledge_dir, "processing", "parsers")): subsystems["Parser Engine"] = True
    if os.path.exists(os.path.join(knowledge_dir, "extractors")): subsystems["Extractor Engine"] = True
    if os.path.exists(os.path.join(knowledge_dir, "normalization")): subsystems["Normalization Engine"] = True
    if os.path.exists(os.path.join(knowledge_dir, "catalog")): subsystems["Resource Catalog"] = True
    if os.path.exists(os.path.join(knowledge_dir, "relationships")): subsystems["Relationship Catalog"] = True
    if os.path.exists(os.path.join(knowledge_dir, "rules")): subsystems["Rule Catalog"] = True
    if os.path.exists(os.path.join(knowledge_dir, "graph")): subsystems["Knowledge Graph"] = True
    if os.path.exists(os.path.join(knowledge_dir, "service")): subsystems["Knowledge Service"] = True
    if os.path.exists(os.path.join(knowledge_dir, "snapshot")): subsystems["Snapshot Manager"] = True
    if os.path.exists(os.path.join(knowledge_dir, "search")): subsystems["Search Engine"] = True
    
    # Analyze all files
    for root, dirs, files in os.walk(knowledge_dir):
        for file in files:
            if not file.endswith(".py"):
                continue
            path = os.path.join(root, file)
            
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Phase 8
            for i, line in enumerate(content.split("\n")):
                if keywords_p8.search(line):
                    code_quality_issues.append(f"{path}:{i+1} - {line.strip()}")
                
                # Simple hardcoded detection for AWS
                if "arn:aws:" in line or "us-east-1" in line or "TODO:" in line:
                    hardcoded.append(f"{path}:{i+1} - {line.strip()}")
                    
                if "import" in line:
                    if "knowledge." in line:
                        # rough dependency check
                        pass

            # AST Analysis
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        for stmt in node.body:
                            if isinstance(stmt, ast.Raise) and isinstance(stmt.exc, ast.Name) and stmt.exc.id == "NotImplementedError":
                                not_implemented_methods.append(f"{path}:{node.name}")
                            if isinstance(stmt, ast.Raise) and isinstance(stmt.exc, ast.Call) and isinstance(stmt.exc.func, ast.Name) and stmt.exc.func.id == "NotImplementedError":
                                not_implemented_methods.append(f"{path}:{node.name}")
            except SyntaxError:
                pass

    print("--- Phase 1: Architecture ---")
    for k, v in subsystems.items():
        print(f"{k}: {'Exists' if v else 'Missing'}")
        
    print("\n--- Phase 2: Packages ---")
    print(f"Missing __init__.py in {len(missing_init)} directories.")
    
    print("\n--- Phase 3: APIs ---")
    print(f"NotImplemented methods: {len(not_implemented_methods)}")
    
    print("\n--- Phase 8: Code Quality ---")
    print(f"Issues found: {len(code_quality_issues)}")
    
    with open("audit_out.txt", "w") as f:
        f.write("Code Quality Issues:\n")
        f.write("\n".join(code_quality_issues))
        f.write("\n\nNot Implemented Methods:\n")
        f.write("\n".join(not_implemented_methods))

if __name__ == '__main__':
    audit()
