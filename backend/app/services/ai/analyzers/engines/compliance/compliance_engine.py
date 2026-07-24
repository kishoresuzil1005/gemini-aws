"""
O(N) Engine for aggregating Security Findings into Compliance Reports.
"""
import time
import uuid
from typing import List, Dict
from app.services.ai.analyzers.engines.security.security_models import (
    SecurityFinding, ComplianceFramework
)
from app.services.ai.analyzers.engines.compliance.compliance_models import (
    ComplianceReport, ComplianceResult, ComplianceSummary, 
    FrameworkStatistics, ControlStatistics, CoverageSummary, ComplianceScore,
    ComplianceStatus, ControlSeverity, ComplianceRequirement
)
from app.services.ai.analyzers.engines.compliance.compliance_registry import ComplianceRegistry

class ComplianceEngine:
    """
    Stateless, thread-safe aggregator for Compliance evaluation.
    """
    def __init__(self, registry: ComplianceRegistry = None):
        self.registry = registry or ComplianceRegistry()
        
    def _calculate_score(self, controls_stats: ControlStatistics) -> ComplianceScore:
        if controls_stats.total == 0:
            return ComplianceScore(score=0.0, grade="N/A")
            
        pass_ratio = controls_stats.passed / controls_stats.total
        score = round(pass_ratio * 100, 2)
        
        if score >= 90: grade = "A"
        elif score >= 80: grade = "B"
        elif score >= 70: grade = "C"
        elif score >= 60: grade = "D"
        else: grade = "F"
        
        return ComplianceScore(score=score, grade=grade)

    def _aggregate_statistics(self, requirements: List[ComplianceRequirement]) -> FrameworkStatistics:
        stats = ControlStatistics(total=0, passed=0, failed=0, warning=0, skipped=0, manual=0)
        sev_dist = {ControlSeverity.CRITICAL: 0, ControlSeverity.HIGH: 0, ControlSeverity.MEDIUM: 0, ControlSeverity.LOW: 0, ControlSeverity.INFO: 0}
        
        total_ev = 0
        
        # Flatten stats
        passed, failed, warning, skipped, manual, total = 0, 0, 0, 0, 0, 0
        for req in requirements:
            for ctl in req.controls:
                total += 1
                if ctl.status == ComplianceStatus.PASSED: passed += 1
                elif ctl.status == ComplianceStatus.FAILED: failed += 1
                elif ctl.status == ComplianceStatus.WARNING: warning += 1
                elif ctl.status == ComplianceStatus.SKIPPED: skipped += 1
                elif ctl.status == ComplianceStatus.MANUAL: manual += 1
                
                sev_dist[ctl.severity] += 1
                total_ev += len(ctl.evidence)
                
        controls_stats = ControlStatistics(total=total, passed=passed, failed=failed, warning=warning, skipped=skipped, manual=manual)
        
        # We assume evaluated resources is approx equivalent to evidence count for high-level coverage
        coverage = CoverageSummary(percentage=100.0 if total > 0 else 0.0, evaluated_resources=total_ev)
        
        score = self._calculate_score(controls_stats)
        
        return FrameworkStatistics(
            controls=controls_stats,
            coverage=coverage,
            score=score,
            severity_distribution=sev_dist
        )

    def generate_report(self, findings: List[SecurityFinding]) -> ComplianceReport:
        # Group findings by framework in O(N)
        framework_bins: Dict[ComplianceFramework, List[SecurityFinding]] = {}
        for fw in self.registry.list_frameworks():
            framework_bins[fw] = []
            
        for f in findings:
            for fw in f.compliance_mapping:
                if fw in framework_bins:
                    framework_bins[fw].append(f)
                    
        results = []
        global_passed, global_failed, global_warning, global_skipped, global_total = 0, 0, 0, 0, 0
        
        for fw, fw_findings in framework_bins.items():
            fw_def = self.registry.get_framework(fw)
            if not fw_def: continue
            
            # Sub-engine evaluates specific framework controls
            requirements = fw_def.map_findings(fw_findings)
            
            stats = self._aggregate_statistics(requirements)
            
            global_passed += stats.controls.passed
            global_failed += stats.controls.failed
            global_warning += stats.controls.warning
            global_skipped += stats.controls.skipped
            global_total += stats.controls.total
            
            results.append(ComplianceResult(
                framework=fw,
                version=fw_def.get_version(),
                requirements=requirements,
                statistics=stats
            ))
            
        global_stats = ControlStatistics(
            total=global_total, passed=global_passed, failed=global_failed,
            warning=global_warning, skipped=global_skipped
        )
        global_score = self._calculate_score(global_stats)
        
        summary = ComplianceSummary(
            executive_summary="Enterprise Compliance Aggregation Complete.",
            total_frameworks_evaluated=len(results),
            overall_score=global_score.score,
            global_statistics=global_stats
        )
        
        return ComplianceReport(
            report_id=str(uuid.uuid4()),
            timestamp=time.time(),
            summary=summary,
            results=results,
            recommendations=["Review FAILED controls in high severity domains."]
        )
