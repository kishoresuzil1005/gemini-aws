"""
SOC2 Compliance Framework.
"""
from typing import List, Dict
from app.services.ai.analyzers.engines.compliance.compliance_framework import ComplianceFrameworkDefinition
from app.services.ai.analyzers.engines.compliance.compliance_models import (
    ComplianceFramework, FrameworkVersion, ComplianceRequirement, ComplianceControl,
    ComplianceEvidence, ComplianceStatus, ControlSeverity
)
from app.services.ai.analyzers.engines.security.security_models import SecurityFinding

class SOC2Framework(ComplianceFrameworkDefinition):
    def get_framework_type(self) -> ComplianceFramework:
        return ComplianceFramework.SOC2
        
    def get_version(self) -> FrameworkVersion:
        return FrameworkVersion(version="TSC", year="2017")
        
    def map_findings(self, findings: List[SecurityFinding]) -> List[ComplianceRequirement]:
        reqs_map: Dict[str, ComplianceRequirement] = {
            "CC6": ComplianceRequirement(requirement_id="CC6", title="Logical and Physical Access Controls", description="Access Controls.", status=ComplianceStatus.PASSED, controls=[]),
            "CC7": ComplianceRequirement(requirement_id="CC7", title="System Operations", description="Monitoring and incident response.", status=ComplianceStatus.PASSED, controls=[])
        }
        
        for finding in findings:
            target_req = "CC7" 
            if finding.category in ["IDENTITY", "NETWORK"]: target_req = "CC6"
            
            evidence = ComplianceEvidence(resource_id=finding.resource_id, resource_type=finding.resource_type, status=ComplianceStatus.FAILED, finding_id=finding.rule_id, reason=finding.description)
            req = reqs_map[target_req]
            existing_ctl = next((c for c in req.controls if c.control_id == finding.rule_id), None)
            
            if existing_ctl:
                new_evidence = list(existing_ctl.evidence) + [evidence]
                idx = req.controls.index(existing_ctl)
                req.controls[idx] = ComplianceControl(control_id=existing_ctl.control_id, title=existing_ctl.title, description=existing_ctl.description, severity=existing_ctl.severity, status=ComplianceStatus.FAILED, evidence=new_evidence)
            else:
                new_ctl = ComplianceControl(control_id=finding.rule_id, title=finding.rule_name, description=finding.description, severity=ControlSeverity(finding.base_severity.value), status=ComplianceStatus.FAILED, evidence=[evidence])
                req.controls.append(new_ctl)
                
        final_reqs = []
        for key, req in reqs_map.items():
            if len(req.controls) > 0:
                has_failure = any(c.status == ComplianceStatus.FAILED for c in req.controls)
                final_reqs.append(ComplianceRequirement(requirement_id=req.requirement_id, title=req.title, description=req.description, status=ComplianceStatus.FAILED if has_failure else ComplianceStatus.PASSED, controls=req.controls))
        return final_reqs
