"""
Ansible Remediation Generator.
"""
from typing import Optional
from app.services.ai.analyzers.engines.security.security_models import SecurityFinding
from app.services.ai.analyzers.engines.remediation.remediation_generator import RemediationGenerator
from app.services.ai.analyzers.engines.remediation.remediation_models import (
    RemediationStep, RollbackPlan, AnsibleTask, ValidationStep, RollbackMode
)

class AnsibleGenerator(RemediationGenerator):
    def get_format(self) -> str:
        return "ANSIBLE"
        
    def generate(self, finding: SecurityFinding) -> Optional[RemediationStep]:
        yaml_content = f"- name: Fix {finding.rule_id}\n  amazon.aws.s3_bucket:\n    name: {finding.resource_id}\n    encryption: AES256"
        rollback_yaml = f"- name: Revert {finding.rule_id}\n  amazon.aws.s3_bucket:\n    name: {finding.resource_id}\n    encryption: none"
        
        cmd = AnsibleTask(yaml=yaml_content, module="amazon.aws.s3_bucket", description="Ansible Playbook Task")
        rollback_cmd = AnsibleTask(yaml=rollback_yaml, module="amazon.aws.s3_bucket", description="Rollback Task")
        
        return RemediationStep(
            name="Execute Ansible Playbook",
            description=f"Ansible task for {finding.rule_id}",
            actions=[cmd],
            validation=[ValidationStep(description="Check mode", command="ansible-playbook playbook.yml --check")],
            rollback=RollbackPlan(mode=RollbackMode.AUTOMATIC, commands=[rollback_cmd], description="Revert task")
        )
