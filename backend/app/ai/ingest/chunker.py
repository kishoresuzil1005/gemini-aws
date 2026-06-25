import os
import json
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

CLEAN_DIR = DATA_DIR / "clean"
CHUNKS_DIR = DATA_DIR / "chunks"

CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 100) -> list:
    """Splits text into chunks of specified size with overlap."""
    chunks = []
    if not text:
        return chunks
        
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        # Advance by size minus overlap
        start += (chunk_size - chunk_overlap)
        
        # If the next start position is near the end, index remaining and break
        if start >= len(text) or len(text) - start <= chunk_overlap:
            if start < len(text):
                chunks.append(text[start:])
            break
    return chunks

def process_clean_docs():
    print(f"[CHUNKER] Reading clean files from: {CLEAN_DIR}")
    print(f"[CHUNKER] Writing chunked JSON files to: {CHUNKS_DIR}")

    if not CLEAN_DIR.exists():
        print(f"[CHUNKER] Error: CLEAN_DIR {CLEAN_DIR} does not exist!")
        return

    txt_files = list(CLEAN_DIR.glob("*.txt"))
    if not txt_files:
        print(f"[CHUNKER] No text files found in {CLEAN_DIR}")
        return

    for txt_file in txt_files:
        content = txt_file.read_text(encoding="utf-8", errors="ignore")
        text_chunks = chunk_text(content, chunk_size=500, chunk_overlap=100)
        
        chunk_dicts = []
        for idx, chunk_content in enumerate(text_chunks):
            chunk_dicts.append({
                "id": f"{txt_file.stem}_chunk_{idx}",
                "content": chunk_content,
                "metadata": {
                    "source": txt_file.name,
                    "chunk_index": idx
                }
            })
            
        output_file = CHUNKS_DIR / f"{txt_file.stem}_chunks.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(chunk_dicts, f, indent=2, ensure_ascii=False)
            
        print(f"[CHUNKER] Chunked {txt_file.name} into {len(text_chunks)} parts: {output_file.name}")

if __name__ == "__main__":
    process_clean_docs()
