#!/bin/bash
STEPS="/home/suzil/.gemini/antigravity/brain/050b584c-99ef-40a2-98ae-ecb204aa2e5e/.system_generated/steps"
DOCS="/home/suzil/Downloads/cloudops (1)/backend/app/services/ai/cloud_docs"

# aws_architecture
cp "$STEPS/343/content.md" "$DOCS/aws_architecture/well_architected_framework.txt"
cp "$STEPS/344/content.md" "$DOCS/aws_architecture/operational_excellence_pillar.txt"
cp "$STEPS/346/content.md" "$DOCS/aws_architecture/reliability_pillar.txt"
cp "$STEPS/347/content.md" "$DOCS/aws_architecture/performance_efficiency_pillar.txt"
cp "$STEPS/349/content.md" "$DOCS/aws_architecture/sustainability_pillar.txt"
cp "$STEPS/385/content.md" "$DOCS/aws_architecture/migration_strategies.txt"
cp "$STEPS/386/content.md" "$DOCS/aws_architecture/disaster_recovery.txt"
cp "$STEPS/387/content.md" "$DOCS/aws_architecture/prescriptive_guidance.txt"

# aws_security
cp "$STEPS/345/content.md" "$DOCS/aws_security/security_pillar.txt"
cp "$STEPS/353/content.md" "$DOCS/aws_security/security_reference_architecture.txt"
cp "$STEPS/354/content.md" "$DOCS/aws_security/iam_best_practices.txt"
cp "$STEPS/355/content.md" "$DOCS/aws_security/security_hub.txt"
cp "$STEPS/356/content.md" "$DOCS/aws_security/guardduty.txt"
cp "$STEPS/357/content.md" "$DOCS/aws_security/waf_developer_guide.txt"

# aws_governance
cp "$STEPS/361/content.md" "$DOCS/aws_governance/aws_organizations.txt"
cp "$STEPS/362/content.md" "$DOCS/aws_governance/control_tower.txt"
cp "$STEPS/363/content.md" "$DOCS/aws_governance/landing_zone_accelerator.txt"

# kubernetes
cp "$STEPS/364/content.md" "$DOCS/kubernetes/eks_best_practices.txt"
cp "$STEPS/365/content.md" "$DOCS/kubernetes/eks_user_guide.txt"

# aws_finops
cp "$STEPS/348/content.md" "$DOCS/aws_finops/cost_optimization_pillar.txt"
cp "$STEPS/369/content.md" "$DOCS/aws_finops/cost_management_user_guide.txt"
cp "$STEPS/370/content.md" "$DOCS/aws_finops/savings_plans.txt"
cp "$STEPS/371/content.md" "$DOCS/aws_finops/compute_optimizer.txt"
cp "$STEPS/372/content.md" "$DOCS/aws_finops/trusted_advisor.txt"

# aws_operations
cp "$STEPS/373/content.md" "$DOCS/aws_operations/vpc_user_guide.txt"
cp "$STEPS/375/content.md" "$DOCS/aws_operations/resilience_hub.txt"
cp "$STEPS/376/content.md" "$DOCS/aws_operations/cloudwatch_user_guide.txt"
cp "$STEPS/384/content.md" "$DOCS/aws_operations/cloud_adoption_framework.txt"

echo "=== Copy complete ==="
echo ""
echo "aws_architecture:"
ls -la "$DOCS/aws_architecture/"
echo ""
echo "aws_security:"
ls -la "$DOCS/aws_security/"
echo ""
echo "aws_finops:"
ls -la "$DOCS/aws_finops/"
echo ""
echo "aws_governance:"
ls -la "$DOCS/aws_governance/"
echo ""
echo "kubernetes:"
ls -la "$DOCS/kubernetes/"
echo ""
echo "aws_operations:"
ls -la "$DOCS/aws_operations/"
