import os
from typing import List, Dict, Any

class DocumentLoader:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
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

        words = text.split()
        total_words = len(words)
        
        i = 0
        chunk_idx = 0
        while i < total_words:
            # Take a slice of words
            end = min(i + self.chunk_size, total_words)
            chunk_words = words[i:end]
            chunk_text = " ".join(chunk_words)
            
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = chunk_idx
            
            chunks.append({
                "id": f"{source}_chunk_{chunk_idx}",
                "content": chunk_text,
                "metadata": chunk_metadata
            })
            
            chunk_idx += 1
            # Step forward with overlap
            i += (self.chunk_size - self.chunk_overlap)
            if i >= total_words or (end == total_words):
                break
                
        return chunks
