#!/bin/bash
STEPS="/home/suzil/.gemini/antigravity/brain/050b584c-99ef-40a2-98ae-ecb204aa2e5e/.system_generated/steps"
DOCS="/home/suzil/Downloads/cloudops (1)/backend/app/services/ai/cloud_docs"

# Security deep-dive docs
cp "$STEPS/478/content.md" "$DOCS/aws_security/security_foundations.txt"
cp "$STEPS/479/content.md" "$DOCS/aws_security/iam_access_policies.txt"
cp "$STEPS/480/content.md" "$DOCS/aws_security/kms_overview.txt"
cp "$STEPS/481/content.md" "$DOCS/aws_security/security_hub_standards.txt"
cp "$STEPS/482/content.md" "$DOCS/aws_security/guardduty_findings.txt"
cp "$STEPS/483/content.md" "$DOCS/aws_security/incident_response.txt"
cp "$STEPS/485/content.md" "$DOCS/aws_security/hipaa_on_aws.txt"
cp "$STEPS/490/content.md" "$DOCS/aws_security/ddos_best_practices.txt"
cp "$STEPS/491/content.md" "$DOCS/aws_security/cis_benchmarks.txt"
cp "$STEPS/492/content.md" "$DOCS/aws_security/zero_trust_architecture.txt"
cp "$STEPS/493/content.md" "$DOCS/aws_security/kms_best_practices.txt"
cp "$STEPS/494/content.md" "$DOCS/aws_security/infrastructure_protection.txt"
cp "$STEPS/495/content.md" "$DOCS/aws_security/data_protection.txt"
cp "$STEPS/496/content.md" "$DOCS/aws_security/aws_security_introduction.txt"
cp "$STEPS/487/content.md" "$DOCS/aws_security/iam_roles.txt"

echo "=== Security docs copied ==="
ls -la "$DOCS/aws_security/"
echo ""
echo "=== Terraform docs ==="
ls -la "$DOCS/terraform/"
echo ""
echo "=== All categories ==="
for cat in aws aws_architecture aws_security aws_finops aws_governance aws_operations kubernetes terraform; do
  count=$(ls "$DOCS/$cat/" 2>/dev/null | wc -l)
  echo "  $cat: $count files"
done
