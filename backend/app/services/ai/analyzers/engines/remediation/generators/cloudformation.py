"""
CloudFormation Remediation Generator.
"""
from typing import Optional
from app.services.ai.analyzers.engines.security.security_models import SecurityFinding
from app.services.ai.analyzers.engines.remediation.remediation_generator import RemediationGenerator
from app.services.ai.analyzers.engines.remediation.remediation_models import (
    RemediationStep, RollbackPlan, CloudFormationResource, ValidationStep, RollbackMode
)

class CloudFormationGenerator(RemediationGenerator):
    def get_format(self) -> str:
        return "CLOUDFORMATION"
        
    def generate(self, finding: SecurityFinding) -> Optional[RemediationStep]:
        yaml_content = f"Resources:\n  MyResource:\n    Type: AWS::S3::Bucket\n    Properties:\n      BucketEncryption:\n        ServerSideEncryptionConfiguration:\n          - ServerSideEncryptionByDefault:\n              SSEAlgorithm: AES256"
        rollback_yaml = f"Resources:\n  MyResource:\n    Type: AWS::S3::Bucket\n    Properties:\n      BucketName: {finding.resource_id}"
        
        cmd = CloudFormationResource(yaml=yaml_content, resource_type="AWS::S3::Bucket", description="YAML snippet")
        rollback_cmd = CloudFormationResource(yaml=rollback_yaml, resource_type="AWS::S3::Bucket", description="Rollback YAML")
        
        return RemediationStep(
            name="Apply CloudFormation YAML",
            description=f"CloudFormation snippet for {finding.rule_id}",
            actions=[cmd],
            validation=[ValidationStep(description="Validate template", command="aws cloudformation validate-template")],
            rollback=RollbackPlan(mode=RollbackMode.AUTOMATIC, commands=[rollback_cmd], description="Revert YAML")
        )
