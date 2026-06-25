#!/usr/bin/env python3
"""Copy downloaded AWS docs from cache to the cloud_docs directories."""
import shutil
import os

STEPS = "/home/suzil/.gemini/antigravity/brain/050b584c-99ef-40a2-98ae-ecb204aa2e5e/.system_generated/steps"
BASE = os.path.join(os.path.dirname(__file__), "app", "services", "ai", "cloud_docs")

copies = [
    # Well-Architected Framework pillars → aws_architecture
    (f"{STEPS}/343/content.md", f"{BASE}/aws_architecture/well_architected_framework.txt"),
    (f"{STEPS}/344/content.md", f"{BASE}/aws_architecture/operational_excellence_pillar.txt"),
    (f"{STEPS}/346/content.md", f"{BASE}/aws_architecture/reliability_pillar.txt"),
    (f"{STEPS}/347/content.md", f"{BASE}/aws_architecture/performance_efficiency_pillar.txt"),
    (f"{STEPS}/349/content.md", f"{BASE}/aws_architecture/sustainability_pillar.txt"),
    (f"{STEPS}/385/content.md", f"{BASE}/aws_architecture/migration_strategies.txt"),
    (f"{STEPS}/386/content.md", f"{BASE}/aws_architecture/disaster_recovery.txt"),
    (f"{STEPS}/387/content.md", f"{BASE}/aws_architecture/prescriptive_guidance.txt"),
    # Security
    (f"{STEPS}/345/content.md", f"{BASE}/aws_security/security_pillar.txt"),
    (f"{STEPS}/353/content.md", f"{BASE}/aws_security/security_reference_architecture.txt"),
    (f"{STEPS}/354/content.md", f"{BASE}/aws_security/iam_best_practices.txt"),
    (f"{STEPS}/355/content.md", f"{BASE}/aws_security/security_hub.txt"),
    (f"{STEPS}/356/content.md", f"{BASE}/aws_security/guardduty.txt"),
    (f"{STEPS}/357/content.md", f"{BASE}/aws_security/waf_developer_guide.txt"),
    # Governance
    (f"{STEPS}/361/content.md", f"{BASE}/aws_governance/aws_organizations.txt"),
    (f"{STEPS}/362/content.md", f"{BASE}/aws_governance/control_tower.txt"),
    (f"{STEPS}/363/content.md", f"{BASE}/aws_governance/landing_zone_accelerator.txt"),
    # Kubernetes
    (f"{STEPS}/364/content.md", f"{BASE}/kubernetes/eks_best_practices.txt"),
    (f"{STEPS}/365/content.md", f"{BASE}/kubernetes/eks_user_guide.txt"),
    # FinOps
    (f"{STEPS}/348/content.md", f"{BASE}/aws_finops/cost_optimization_pillar.txt"),
    (f"{STEPS}/369/content.md", f"{BASE}/aws_finops/cost_management_user_guide.txt"),
    (f"{STEPS}/370/content.md", f"{BASE}/aws_finops/savings_plans.txt"),
    (f"{STEPS}/371/content.md", f"{BASE}/aws_finops/compute_optimizer.txt"),
    (f"{STEPS}/372/content.md", f"{BASE}/aws_finops/trusted_advisor.txt"),
    # Operations
    (f"{STEPS}/373/content.md", f"{BASE}/aws_operations/vpc_user_guide.txt"),
    (f"{STEPS}/375/content.md", f"{BASE}/aws_operations/resilience_hub.txt"),
    (f"{STEPS}/376/content.md", f"{BASE}/aws_operations/cloudwatch_user_guide.txt"),
    (f"{STEPS}/384/content.md", f"{BASE}/aws_operations/cloud_adoption_framework.txt"),
]

ok = 0
fail = 0
for src, dst in copies:
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        size = os.path.getsize(dst)
        print(f"  OK  {os.path.basename(dst):50s}  ({size:,} bytes)")
        ok += 1
    except Exception as e:
        print(f"FAIL  {os.path.basename(dst):50s}  {e}")
        fail += 1

print(f"\nCopied {ok} files, {fail} failures.")
