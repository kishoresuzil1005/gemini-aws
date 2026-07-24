"""
Terraform Remediation Generator.
"""
from typing import Optional
from app.services.ai.analyzers.engines.security.security_models import SecurityFinding
from app.services.ai.analyzers.engines.remediation.remediation_generator import RemediationGenerator
from app.services.ai.analyzers.engines.remediation.remediation_models import (
    RemediationStep, RollbackPlan, TerraformResource, ValidationStep, RollbackMode
)

class TerraformGenerator(RemediationGenerator):
    def get_format(self) -> str:
        return "TERRAFORM"
        
    def generate(self, finding: SecurityFinding) -> Optional[RemediationStep]:
        hcl = f'resource "aws_s3_bucket" "{finding.resource_id}" {{\n  bucket = "{finding.resource_id}"\n  # Added missing encryption\n  server_side_encryption_configuration {{\n    rule {{\n      apply_server_side_encryption_by_default {{\n        sse_algorithm = "AES256"\n      }}\n    }}\n  }}\n}}'
        rollback_hcl = f'resource "aws_s3_bucket" "{finding.resource_id}" {{\n  bucket = "{finding.resource_id}"\n  # Reverted encryption\n}}'
        
        cmd = TerraformResource(hcl=hcl, resource_type="aws_s3_bucket", description="HCL for encryption")
        rollback_cmd = TerraformResource(hcl=rollback_hcl, resource_type="aws_s3_bucket", description="Rollback HCL")
        
        return RemediationStep(
            name="Apply Terraform HCL",
            description=f"Terraform resource block for {finding.rule_id}",
            actions=[cmd],
            validation=[ValidationStep(description="Run terraform plan", command="terraform plan")],
            rollback=RollbackPlan(mode=RollbackMode.AUTOMATIC, commands=[rollback_cmd], description="Revert to previous HCL")
        )
