import os
from typing import List, Dict, Any

def chunk_text(text: str, size: int = 500) -> List[str]:
    return [
        text[i:i+size]
        for i in range(
            0,
            len(text),
            size
        )
    ]

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
            for file in files:
                if file.endswith((".txt", ".md", ".json")):
                    file_path = os.path.join(root, file)
                    chunks.extend(self.load_and_split_file(file_path))
        return chunks

    def load_and_split_file(self, file_path: str) -> List[Dict[str, Any]]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            filename = os.path.basename(file_path)
            return self.split_text(content, source=filename)
        except Exception as e:
            print(f"[DOCUMENT LOADER] Error reading file {file_path}: {e}")
            return []

    def split_text(self, text: str, source: str = "unknown", extra_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        chunks = []
        if not text:
            return chunks

        metadata = extra_metadata or {}
        metadata["source"] = source

        text_chunks = chunk_text(text, size=self.chunk_size)
        
        for chunk_idx, chunk_text_content in enumerate(text_chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = chunk_idx
            
            chunks.append({
                "id": f"{source}_chunk_{chunk_idx}",
                "content": chunk_text_content,
                "metadata": chunk_metadata
            })
                
        return chunks
