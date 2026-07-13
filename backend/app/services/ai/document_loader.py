import os
import fitz  # PyMuPDF
from typing import List, Dict, Any

def chunk_text(text: str, size: int = 500, overlap: int = 100) -> List[str]:
    chunks = []
    if not text:
        return chunks
    if len(text) <= size:
        return [text]
        
    start = 0
    while start < len(text):
        chunks.append(text[start:start+size])
        start += (size - overlap)
    return chunks

class DocumentLoader:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_and_split_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        chunks = []
        if not os.path.exists(directory_path):
            print(f"[DOCUMENT LOADER] Directory {directory_path} does not exist.")
            return chunks

        for root, _, files in os.walk(directory_path):
            category = os.path.basename(root)
            for file in files:
                if file.endswith((".txt", ".md", ".json", ".pdf")):

                    file_path = os.path.join(root, file)

                    print(f"[LOADING] {file}")

                    file_chunks = self.load_and_split_file(file_path, category=category)

                    print(f"[CHUNKS] {file} -> {len(file_chunks)}")

                    chunks.extend(file_chunks)
        return chunks

    def load_and_split_file(self, file_path: str, category: str = "default") -> List[Dict[str, Any]]:
        try:
            content = ""
            if file_path.endswith(".pdf"):
                with fitz.open(file_path) as doc:
                    for page in doc:
                        content += page.get_text() + "\n"
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            
            filename = os.path.basename(file_path)
            return self.split_text(content, source=filename, extra_metadata={"category": category})
        except Exception as e:
            print(f"[DOCUMENT LOADER] Error reading file {file_path}: {e}")
            return []

    def split_text(self, text: str, source: str = "unknown", extra_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        chunks = []
        if not text:
            return chunks

        metadata = extra_metadata or {}
        metadata["source"] = source

        text_chunks = chunk_text(text, size=self.chunk_size, overlap=self.chunk_overlap)
        
        for chunk_idx, chunk_text_content in enumerate(text_chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = chunk_idx
            
            chunks.append({
                "id": f"{source}_chunk_{chunk_idx}",
                "content": chunk_text_content,
                "metadata": chunk_metadata
            })
                
        return chunk