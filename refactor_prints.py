import os
import libcst as cst
import libcst.matchers as m

class PrintToLoggerTransformer(cst.CSTTransformer):
    def __init__(self):
        super().__init__()
        self.replaced_any = False

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.CSTNode:
        is_print = False
        if m.matches(original_node.func, m.Name("print")) or m.matches(original_node.func, m.Name("pprint")):
            is_print = True
        elif m.matches(original_node.func, m.Attribute(value=m.Name("console"), attr=m.Name("print"))):
            is_print = True
        elif m.matches(original_node.func, m.Attribute(value=m.Name("rich"), attr=m.Name("print"))):
            is_print = True

        if is_print:
            self.replaced_any = True
            args = list(updated_node.args)
            
            if len(args) == 0:
                return updated_node.with_changes(
                    func=cst.Attribute(value=cst.Name("logger"), attr=cst.Name("debug")),
                    args=[cst.Arg(cst.SimpleString('""'))]
                )
            elif len(args) == 1:
                # Need to strip out keyword args if any, like sep, end, file, flush
                # But for a single arg, it's safe to just use logger.debug(arg)
                return updated_node.with_changes(
                    func=cst.Attribute(value=cst.Name("logger"), attr=cst.Name("debug")),
                    args=[args[0]]
                )
            else:
                f_string_parts = []
                for i, arg in enumerate(args):
                    if arg.keyword is not None:
                        # ignore print(..., end="") kwargs
                        continue
                        
                    if m.matches(arg.value, m.SimpleString()):
                        val = arg.value.value
                        if len(val) >= 2 and val[0] in ('"', "'") and val[-1] in ('"', "'"):
                            val = val[1:-1]
                        # escape brackets
                        val = val.replace("{", "{{").replace("}", "}}")
                        f_string_parts.append(cst.FormattedStringText(val))
                    elif m.matches(arg.value, m.FormattedString()):
                        # If it's already an f-string, unwrap its parts
                        for part in arg.value.parts:
                            f_string_parts.append(part)
                    else:
                        f_string_parts.append(cst.FormattedStringExpression(arg.value))
                    
                    if i < len(args) - 1:
                        f_string_parts.append(cst.FormattedStringText(" "))
                        
                fstring = cst.FormattedString(parts=tuple(f_string_parts), start='f"', end='"')
                return updated_node.with_changes(
                    func=cst.Attribute(value=cst.Name("logger"), attr=cst.Name("debug")),
                    args=[cst.Arg(fstring)]
                )
                
        return updated_node

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        if self.replaced_any:
            # simple check by text if already imported
            code = updated_node.code if hasattr(updated_node, "code") else ""
            # Because we can't easily check code from updated_node.body directly as a string, 
            # let's just insert it safely or check CST
            has_logger_import = False
            for stmt in updated_node.body:
                if m.matches(stmt, m.SimpleStatementLine()):
                    for b in stmt.body:
                        if m.matches(b, m.ImportFrom(module=m.Attribute(value=m.Attribute(value=m.Name("app"), attr=m.Name("core")), attr=m.Name("logging")))):
                            has_logger_import = True
                            
            if not has_logger_import:
                import_stmt = cst.parse_statement("from app.core.logging import get_logger\n")
                logger_stmt = cst.parse_statement("logger = get_logger(__name__)\n")
                
                body = list(updated_node.body)
                insert_idx = 0
                if body and m.matches(body[0], m.SimpleStatementLine(body=[m.Expr(value=m.SimpleString())])):
                    insert_idx = 1
                    
                body.insert(insert_idx, logger_stmt)
                body.insert(insert_idx, import_stmt)
                
                return updated_node.with_changes(body=tuple(body))
                
        return updated_node

def refactor_file(filepath):
    with open(filepath, "r") as f:
        source = f.read()

    if "print(" not in source and "print (" not in source:
        return False
        
    try:
        module = cst.parse_module(source)
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return False
        
    transformer = PrintToLoggerTransformer()
    new_module = module.visit(transformer)
    
    if transformer.replaced_any:
        with open(filepath, "w") as f:
            f.write(new_module.code)
        return True
    return False

if __name__ == "__main__":
    count = 0
    for root, _, files in os.walk("backend/app"):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                if "core/logging" in filepath:
                    continue
                if refactor_file(filepath):
                    count += 1
    print(f"Refactored {count} files.")
