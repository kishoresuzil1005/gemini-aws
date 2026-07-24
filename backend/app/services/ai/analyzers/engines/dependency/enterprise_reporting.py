"""
Enterprise Reporting Module.
Produces deterministic, JSON-serializable reports for executive dashboards and metrics.
"""
from typing import Dict, List, Any
from app.services.ai.analyzers.engines.dependency.dependency_models import DependencyAnalysis
import json

class EnterpriseReportingService:
    
    @classmethod
    def generate_report(cls, findings: List[DependencyAnalysis], telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compiles the findings into an Executive SRE Report.
        """
        # Top SPOFs by Blast Radius
        spofs = [f for f in findings if f.is_spof]
        spofs_sorted = sorted(spofs, key=lambda x: x.blast_radius, reverse=True)[:10]
        
        # Most Critical Resources
        critical = [f for f in findings if f.business_criticality in ["Mission Critical", "Production"]]
        critical_sorted = sorted(critical, key=lambda x: x.risk_score, reverse=True)[:10]
        
        # Incident Impact Aggregation
        total_high_risk = len([f for f in findings if f.risk_score >= 80])
        total_cycles = sum([len(f.cycles) for f in findings])
        
        report = {
            "health_summary": {
                "total_resources_analyzed": len(findings),
                "high_risk_resources": total_high_risk,
                "total_spofs_detected": len(spofs),
                "circular_dependencies": total_cycles
            },
            "top_risks": [
                {
                    "node_id": f.node_id,
                    "risk_score": f.risk_score,
                    "criticality": f.business_criticality,
                    "blast_radius": f.blast_radius
                } for f in critical_sorted
            ],
            "most_dangerous_spofs": [
                {
                    "node_id": f.node_id,
                    "blast_radius": f.blast_radius,
                    "downstream_impact": f.critical_path_downstream
                } for f in spofs_sorted
            ],
            "telemetry": telemetry
        }
        
        return report

    @classmethod
    def to_json(cls, report: Dict[str, Any]) -> str:
        return json.dumps(report, indent=2)
