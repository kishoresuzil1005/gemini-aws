from pathlib import Path
from bs4 import BeautifulSoup

AWS_DIR = Path(__file__).parent / "cloud_docs" / "aws"

# Also fallback to absolute directories for redundancy
if not AWS_DIR.exists():
    AWS_DIR = Path("/backend/app/services/ai/cloud_docs/aws")

print(f"Targeting AWS Docs Directory at: {AWS_DIR}")

if AWS_DIR.exists():
    for html_file in AWS_DIR.glob("*.html"):
        text_file = html_file.with_suffix(".txt")
        html = html_file.read_text(
            encoding="utf-8",
            errors="ignore"
        )
        soup = BeautifulSoup(
            html,
            "html.parser"
        )
        text = soup.get_text(
            separator="\n"
        )
        text_file.write_text(
            text,
            encoding="utf-8"
        )
        print(
            f"Converted {html_file.name}"
        )
else:
    print("Warning: AWS docs directory does not exist yet at either location.")