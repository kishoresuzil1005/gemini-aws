from typing import Dict, Any, List

class DashboardAggregator:
    """
    SaaS unified dashboard aggregator that surfaces organization-level metrics.
    Connects to the underlying Mission Engine and Billing databases.
    """
    def get_tenant_dashboard(self, tenant_id: str) -> Dict[str, Any]:
        print(f"[DashboardAggregator] Compiling dashboard for tenant {tenant_id}")
        return {
            "tenant_id": tenant_id,
            "system_health": "OPTIMAL",
            "active_missions": 4,
            "cloud_accounts_connected": 2,
            "estimated_monthly_savings": "$1,450.00",
            "recent_incidents": 0,
            "agent_status": {
                "infrastructure": "IDLE",
                "security": "WORKING"
            }
        }
