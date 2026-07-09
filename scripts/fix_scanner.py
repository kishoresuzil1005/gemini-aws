import re

with open("/tmp/scanner.py", "r") as f:
    content = f.read()

# I will write a small python parser to rewrite the append calls.
# Wait, it's easier to just do it via AST or careful manual regex.
# Actually, I can use the libcst library, but I can also just do string replacements.

