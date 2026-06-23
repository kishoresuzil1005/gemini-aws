import os
from app.services.ai.rag_service import RAGService

AWS_DOCS_PATH = "app/services/ai/cloud_docs/aws"

if not os.path.exists(AWS_DOCS_PATH):
    # Try dynamic resolution relative to the script location
    AWS_DOCS_PATH = os.path.join(os.path.dirname(__file__), "app", "services", "ai", "cloud_docs", "aws")

rag = RAGService()
indexed = 0

print(f"Scanning for text files in: {AWS_DOCS_PATH}")

if os.path.exists(AWS_DOCS_PATH):
    for file_name in os.listdir(AWS_DOCS_PATH):
        if not file_name.endswith(".txt"):
            continue

        file_path = os.path.join(AWS_DOCS_PATH, file_name)

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        print(f"Indexing {file_name}...")
        result = rag.index_document(
            title=file_name,
            content=content
        )
        print(result)
        indexed += 1

    print(f"Indexed {indexed} documents successfully!")
else:
    print(f"Error: Path {AWS_DOCS_PATH} does not exist. Please check the directory structure.")
