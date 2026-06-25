import os
from app.services.ai.rag_service import RAGService
from dotenv import load_dotenv

load_dotenv()

CLOUD_DOCS_PATH = os.path.join(os.path.dirname(__file__), "app", "services", "ai", "cloud_docs")

def main():
    rag = RAGService()
    
    directories_to_index = [
        "aws",
        "architecture",
        "security",
        "finops",
        "aws_architecture",
        "aws_security",
        "aws_finops",
        "aws_operations",
        "aws_governance",
        "kubernetes",
        "terraform",
    ]
    total_indexed = 0
    
    for dir_name in directories_to_index:
        dir_path = os.path.join(CLOUD_DOCS_PATH, dir_name)
        if os.path.exists(dir_path):
            print(f"\n--- Indexing {dir_name} documents ---")
            chunks_indexed = rag.index_directory(dir_path)
            total_indexed += chunks_indexed
            print(f"Indexed {chunks_indexed} chunks from {dir_name}.")
        else:
            print(f"\n--- Skipping {dir_name}: Directory not found at {dir_path} ---")
            
    print(f"\nTotal chunks indexed across all directories: {total_indexed}")

if __name__ == "__main__":
    main()
