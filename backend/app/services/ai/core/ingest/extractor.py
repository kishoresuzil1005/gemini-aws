import os
from bs4 import BeautifulSoup
from pathlib import Path

RUNNING_DIR = Path(__file__).resolve().parent

unresolved_paths = [
    "backend/data/aws_docs",
    "data/aws_docs"
]

DATA_DIR = None
for path in unresolved_paths:
    p = RUNNING_DIR
    found = False
    for i in range(5):
        test_path = p / path
        if test_path.exists():
            DATA_DIR = test_path
            found = True
            break
        p = p.parent
    if found:
        break

if not DATA_DIR:
    DATA_DIR = Path("/backend/data/aws_docs")

RAW_DIR = DATA_DIR / "raw"
OUT_DIR = DATA_DIR / "clean"

OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"[EXTRACTOR] Reading raw files from: {RAW_DIR}")
print(f"[EXTRACTOR] Writing clean files to: {OUT_DIR}")

if not RAW_DIR.exists():
    print(f"[EXTRACTOR] Error: RAW_DIR {RAW_DIR} does not exist!")
    exit(1)

html_files = list(RAW_DIR.glob("*.html"))
if not html_files:
    print(f"[EXTRACTOR] No HTML files found in {RAW_DIR}")

for html_file in html_files:
    html = html_file.read_text(
        encoding="utf-8",
        errors="ignore"
    )
    
    soup = BeautifulSoup(
        html,
        "html.parser"
    )
    
    text = soup.get_text(
        separator="\n",
        strip=True
    )
    
    output = OUT_DIR / f"{html_file.stem}.txt"
    output.write_text(
        text,
        encoding="utf-8"
    )
    
    print("Processed:", html_file.name)
