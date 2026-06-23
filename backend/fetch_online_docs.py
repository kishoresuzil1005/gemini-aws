import os
import requests

def download_file(url, output_dir, filename):
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    print(f"Downloading {filename} from {url}...")
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Successfully downloaded {filename}")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")

def main():
    base_dir = os.path.join(os.path.dirname(__file__), "app", "services", "ai", "cloud_docs")
    
    docs = [
        {
            "url": "https://docs.aws.amazon.com/wellarchitected/latest/framework/wellarchitected-framework.pdf",
            "dir": "architecture",
            "filename": "wellarchitected-framework.pdf"
        },
        {
            "url": "https://docs.aws.amazon.com/pdfs/whitepapers/latest/aws-overview/aws-overview.pdf",
            "dir": "architecture",
            "filename": "aws-overview.pdf"
        },
        {
            "url": "https://docs.aws.amazon.com/pdfs/whitepapers/latest/aws-security-incident-response-guide/aws-security-incident-response-guide.pdf",
            "dir": "security",
            "filename": "aws-security-incident-response-guide.pdf"
        },
        {
            "url": "https://docs.aws.amazon.com/pdfs/wellarchitected/latest/cost-optimization-pillar/wellarchitected-cost-optimization-pillar.pdf",
            "dir": "finops",
            "filename": "cost-optimization-pillar.pdf"
        }
    ]

    for doc in docs:
        output_dir = os.path.join(base_dir, doc["dir"])
        download_file(doc["url"], output_dir, doc["filename"])

if __name__ == "__main__":
    main()
