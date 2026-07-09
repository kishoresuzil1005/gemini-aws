import os
import requests
from pathlib import Path

# Foolproof path resolution supporting the docker container execution and direct host execution
RUNNING_DIR = Path(__file__).resolve().parent
# Search upward for backend root or data root
PROJECT_ROOT = RUNNING_DIR
unresolved_paths = [
    "backend/data/aws_docs",
    "data/aws_docs"
]

DATA_DIR = None
for path in unresolved_paths:
    # Try parents of current script folder
    p = RUNNING_DIR
    found = False
    for i in range(5):
        test_path = p / path
        if test_path.exists() or test_path.parent.exists():
            DATA_DIR = test_path
            found = True
            break
        p = p.parent
    if found:
        break

if not DATA_DIR:
    DATA_DIR = Path("/backend/data/aws_docs")

INPUT_FILE = DATA_DIR / "aws_urls.txt"
OUTPUT_DIR = DATA_DIR / "raw"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"[CRAWLER] Loading URLs from: {INPUT_FILE}")
print(f"[CRAWLER] Saving downloaded HTML files to: {OUTPUT_DIR}")

if not INPUT_FILE.exists():
    print(f"[CRAWLER] Error: INPUT_FILE {INPUT_FILE} does not exist!")
    exit(1)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    urls = [u.strip() for u in f if u.strip()]

for idx, url in enumerate(urls):
    try:
        print(f"[CRAWLER] Requesting {url}...")
        r = requests.get(url, timeout=30)
        
        output_file_path = OUTPUT_DIR / f"doc_{idx}.html"
        with open(output_file_path, "w", encoding="utf-8") as fp:
            fp.write(r.text)
            
        print(f"[CRAWLER] Downloaded and saved to: {output_file_path.name}")
        
    except Exception as e:
        print(f"[CRAWLER] Failed: {url} | Error: {e}")
