import os
import requests
from bs4 import BeautifulSoup

# Base directory for cloud docs inside the container
BASE_DIR = os.path.join(os.path.dirname(__file__), "app", "services", "ai", "cloud_docs")

# Ensure all target sub‑directories exist
CATEGORIES = [
    "aws_architecture",
    "aws_security",
    "aws_finops",
    "aws_operations",
    "aws_governance",
    "kubernetes",
    "terraform",
]

for cat in CATEGORIES:
    os.makedirs(os.path.join(BASE_DIR, cat), exist_ok=True)

def save_pdf(content: bytes, out_path: str):
    with open(out_path, "wb") as f:
        f.write(content)

def save_txt(text: str, out_path: str):
    # Clean up whitespace a bit
    cleaned = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(cleaned)

def download_and_store(url: str, category: str, filename: str, is_pdf: bool = False):
    out_dir = os.path.join(BASE_DIR, category)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, filename)
    print(f"Downloading {filename} from {url} into {category} ...")
    try:
        resp = requests.get(url, stream=True, timeout=30)
        resp.raise_for_status()
        if is_pdf or url.lower().endswith('.pdf'):
            # Binary PDF content
            save_pdf(resp.content, out_path)
        else:
            # Assume HTML, convert to plain text
            soup = BeautifulSoup(resp.text, "html.parser")
            # Remove scripts/styles
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text(separator="\n")
            # Save as .txt (force .txt extension regardless of input filename)
            if not out_path.lower().endswith('.txt'):
                out_path = out_path + ".txt"
            save_txt(text, out_path)
        print(f"Successfully saved {filename}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")


def main():
    docs = [
        # ==== Well‑Architected Framework (Architecture) ==== 
        {"url": "https://d1.awsstatic.com/whitepapers/architecture/AWS_Well-Architected_Framework.pdf", "category": "aws_architecture", "filename": "well_architected_framework.pdf", "is_pdf": True},
        {"url": "https://d1.awsstatic.com/whitepapers/architecture/operational_excellence_pillar.pdf", "category": "aws_architecture", "filename": "operational_excellence_pillar.pdf", "is_pdf": True},
        {"url": "https://d1.awsstatic.com/whitepapers/architecture/security_pillar.pdf", "category": "aws_architecture", "filename": "security_pillar.pdf", "is_pdf": True},
        {"url": "https://d1.awsstatic.com/whitepapers/architecture/reliability_pillar.pdf", "category": "aws_architecture", "filename": "reliability_pillar.pdf", "is_pdf": True},
        {"url": "https://d1.awsstatic.com/whitepapers/architecture/performance_efficiency_pillar.pdf", "category": "aws_architecture", "filename": "performance_efficiency_pillar.pdf", "is_pdf": True},
        {"url": "https://d1.awsstatic.com/whitepapers/architecture/cost_optimization_pillar.pdf", "category": "aws_architecture", "filename": "cost_optimization_pillar.pdf", "is_pdf": True},
        {"url": "https://d1.awsstatic.com/whitepapers/architecture/sustainability_pillar.pdf", "category": "aws_architecture", "filename": "sustainability_pillar.pdf", "is_pdf": True},
        # ==== Security Best Practices (Security) ==== 
        {"url": "https://d1.awsstatic.com/whitepapers/security/AWS_Security_Reference_Architecture.pdf", "category": "aws_security", "filename": "security_reference_architecture.pdf", "is_pdf": True},
        {"url": "https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html", "category": "aws_security", "filename": "iam_best_practices.txt"},
        {"url": "https://docs.aws.amazon.com/securityhub/latest/userguide/what-is-securityhub.html", "category": "aws_security", "filename": "security_hub.txt"},
        {"url": "https://docs.aws.amazon.com/guardduty/latest/ug/what-is-guardduty.html", "category": "aws_security", "filename": "guardduty.txt"},
        {"url": "https://docs.aws.amazon.com/waf/latest/developerguide/waf-chapter.html", "category": "aws_security", "filename": "waf_developer_guide.txt"},
        # ==== Multi‑Account & Governance (Governance) ==== 
        {"url": "https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html", "category": "aws_governance", "filename": "aws_organizations.txt"},
        {"url": "https://docs.aws.amazon.com/controltower/latest/userguide/what-is-control-tower.html", "category": "aws_governance", "filename": "control_tower.txt"},
        {"url": "https://docs.aws.amazon.com/solutions/latest/landing-zone-accelerator-on-aws/solution-overview.html", "category": "aws_governance", "filename": "landing_zone_accelerator.txt"},
        # ==== EKS & Kubernetes (Kubernetes) ==== 
        {"url": "https://aws.github.io/aws-eks-best-practices/", "category": "kubernetes", "filename": "eks_best_practices.txt"},
        {"url": "https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html", "category": "kubernetes", "filename": "eks_user_guide.txt"},
        # ==== FinOps / Cost Optimization (FinOps) ==== 
        {"url": "https://docs.aws.amazon.com/cost-management/latest/userguide/what-is-costmanagement.html", "category": "aws_finops", "filename": "cost_management_user_guide.txt"},
        {"url": "https://docs.aws.amazon.com/savingsplans/latest/userguide/what-is-savings-plans.html", "category": "aws_finops", "filename": "savings_plans.txt"},
        {"url": "https://docs.aws.amazon.com/compute-optimizer/latest/ug/what-is-compute-optimizer.html", "category": "aws_finops", "filename": "compute_optimizer.txt"},
        {"url": "https://docs.aws.amazon.com/awssupport/latest/user/trusted-advisor.html", "category": "aws_finops", "filename": "trusted_advisor.txt"},
        # ==== Operations & Architecture (Operations) ==== 
        {"url": "https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html", "category": "aws_operations", "filename": "vpc_user_guide.txt"},
        {"url": "https://d1.awsstatic.com/whitepapers/AWS_Cloud_Adoption_Framework.pdf", "category": "aws_operations", "filename": "cloud_adoption_framework.pdf", "is_pdf": True},
        {"url": "https://d1.awsstatic.com/whitepapers/resilience-hub.pdf", "category": "aws_operations", "filename": "resilience_hub.pdf", "is_pdf": True},
        {"url": "https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html", "category": "aws_operations", "filename": "cloudwatch_user_guide.txt"},
        # ==== Prescriptive Guidance (Architecture) ==== 
        {"url": "https://docs.aws.amazon.com/prescriptive-guidance/latest/home/welcome.html", "category": "aws_architecture", "filename": "prescriptive_guidance_home.txt"},
        {"url": "https://docs.aws.amazon.com/prescriptive-guidance/latest/migration-portfolio-assessment-guide/welcome.html", "category": "aws_architecture", "filename": "migration_strategies.txt"},
        {"url": "https://docs.aws.amazon.com/prescriptive-guidance/latest/recovery-dr-guidance/welcome.html", "category": "aws_architecture", "filename": "disaster_recovery_guidance.txt"},
    ]

    for doc in docs:
        download_and_store(
            url=doc["url"],
            category=doc["category"],
            filename=doc["filename"],
            is_pdf=doc.get("is_pdf", False)
        )

if __name__ == "__main__":
    main()
