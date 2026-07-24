"""
CIS Foundations Compliance Framework.
"""
from typing import List, Dict
from app.services.ai.analyzers.engines.compliance.compliance_framework import ComplianceFrameworkDefinition
from app.services.ai.analyzers.engines.compliance.compliance_models import (
    ComplianceFramework, FrameworkVersion, ComplianceRequirement, ComplianceControl,
    ComplianceEvidence, ComplianceStatus, ControlSeverity
)
from app.services.ai.analyzers.engines.security.security_models import SecurityFinding, SecurityCategory

class CISFramework(ComplianceFrameworkDefinition):
    def get_framework_type(self) -> ComplianceFramework:
        return ComplianceFramework.CIS
        
    def get_version(self) -> FrameworkVersion:
        return FrameworkVersion(version="1.4.0", year="2021")
        
    def map_findings(self, findings: List[SecurityFinding]) -> List[ComplianceRequirement]:
        # CIS groups heavily by IAM, Storage, Logging, Monitoring, Networking
        reqs_map: Dict[str, ComplianceRequirement] = {
            "IAM": ComplianceRequirement(requirement_id="CIS-1", title="Identity and Access Management", description="IAM best practices.", status=ComplianceStatus.PASSED, controls=[]),
            "Storage": ComplianceRequirement(requirement_id="CIS-2", title="Storage", description="Storage security.", status=ComplianceStatus.PASSED, controls=[]),
            "Logging": ComplianceRequirement(requirement_id="CIS-3", title="Logging", description="Logging configuration.", status=ComplianceStatus.PASSED, controls=[]),
            "Monitoring": ComplianceRequirement(requirement_id="CIS-4", title="Monitoring", description="Monitoring rules.", status=ComplianceStatus.PASSED, controls=[]),
            "Networking": ComplianceRequirement(requirement_id="CIS-5", title="Networking", description="Networking best practices.", status=ComplianceStatus.PASSED, controls=[])
        }
        
        # We will create one generic control per finding type for the demonstration of mapping
        for finding in findings:
            target_req = "Networking" # Default
            if finding.category == SecurityCategory.IDENTITY: target_req = "IAM"
            elif finding.category in [SecurityCategory.STORAGE, SecurityCategory.DATABASE]: target_req = "Storage"
            elif finding.category == SecurityCategory.LOGGING: target_req = "Logging"
            elif finding.category == SecurityCategory.MONITORING: target_req = "Monitoring"
            
            # Map rule to a control (in a real system, there'd be a static map of AWS-IAM-001 -> CIS 1.2)
            # Here we map 1:1 rule to control for determinism
            evidence = ComplianceEvidence(
                resource_id=finding.resource_id,
                resource_type=finding.resource_type,
                status=ComplianceStatus.FAILED,
                finding_id=finding.rule_id,
                reason=finding.description
            )
            
            # Find or create control
            req = reqs_map[target_req]
            existing_ctl = next((c for c in req.controls if c.control_id == finding.rule_id), None)
            
            if existing_ctl:
                # Add evidence, update status
                # Tuples in Pydantic V2 immutable objects mean we rebuild the list
                new_evidence = list(existing_ctl.evidence) + [evidence]
                idx = req.controls.index(existing_ctl)
                req.controls[idx] = ComplianceControl(
                    control_id=existing_ctl.control_id,
                    title=existing_ctl.title,
                    description=existing_ctl.description,
                    severity=existing_ctl.severity,
                    status=ComplianceStatus.FAILED,
                    evidence=new_evidence
                )
            else:
                new_ctl = ComplianceControl(
                    control_id=finding.rule_id,
                    title=finding.rule_name,
                    description=f"Map {finding.rule_id} to CIS",
                    severity=ControlSeverity(finding.base_severity.value), # Exact string map (HIGH -> HIGH)
                    status=ComplianceStatus.FAILED,
                    evidence=[evidence]
                )
                req.controls.append(new_ctl)
                
        # Propagate FAIL to Requirement status
        for req in reqs_map.values():
            if any(c.status == ComplianceStatus.FAILED for c in req.controls):
                # Pydantic V2 immutable update (since we didn't freeze inside the dict, we can just rebuild it)
                pass # The reqs_map mutation requires a rebuild
                
        final_reqs = []
        for key, req in reqs_map.items():
            if len(req.controls) > 0:
                has_failure = any(c.status == ComplianceStatus.FAILED for c in req.controls)
                final_reqs.append(ComplianceRequirement(
                    requirement_id=req.requirement_id,
                    title=req.title,
                    description=req.description,
                    status=ComplianceStatus.FAILED if has_failure else ComplianceStatus.PASSED,
                    controls=req.controls
                ))
                
        return final_reqs
