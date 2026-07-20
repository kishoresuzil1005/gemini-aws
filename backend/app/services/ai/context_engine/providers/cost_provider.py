"""CostProvider – fetches simplified cost data from AWS Cost Explorer.

Uses the existing ``CostExplorerAdapter`` that already handles caching
and rate-limit protection.  Adds:
  - Previous month spend
  - 30-day daily breakdown
  - Idle-resource detection (avg daily cost < $0.10)
  - Potential savings estimate

No forecasts are computed here (deferred to CostAnalyzer in Phase 3).
"""

import time
import logging
from typing import Any, Dict, List

from ..base_provider import BaseProvider
from ..common.constants import COST_PROVIDER_ENABLED, TTL_DYNAMIC
from ..common.helpers import flag_enabled
from ..enums import ContextLevel, ProviderScope
from ..request import ContextRequest
from ..resolved_resource import ResolvedResource

logger = logging.getLogger(__name__)

# Idle threshold – resources averaging under $0.10/day are considered idle
IDLE_THRESHOLD_USD_PER_DAY = 0.10


class CostProvider(BaseProvider):
    """Fetches simplified cost data from AWS Cost Explorer."""

    name       = "cost"
    scope      = ProviderScope.DYNAMIC
    priority   = 60
    output_key = "cost"
    cache_ttl  = TTL_DYNAMIC
    version    = "1.0"
    source     = "cost_explorer"
    enabled    = flag_enabled(COST_PROVIDER_ENABLED)

    def supports(self, level: ContextLevel) -> bool:
        return level == ContextLevel.DEEP

    async def fetch(self, resource: ResolvedResource, request: ContextRequest) -> Dict[str, Any]:
        t0 = time.monotonic()
        data = self._fetch_cost(resource.resource_id, request.cost_granularity)
        exec_ms = (time.monotonic() - t0) * 1000
        return self._build_response(data, execution_time_ms=exec_ms)

    # ------------------------------------------------------------------

    def _fetch_cost(self, resource_id: str, granularity: str) -> Dict[str, Any]:
        """
        Use the CostExplorerAdapter to pull current/previous month costs
        and the 30-day daily breakdown.

        Cost Explorer does NOT filter by resource ID without resource-level
        granularity; we use the first cloud account.
        """
        try:
            from app.database import SessionLocal
            from app.models import CloudAccountDB
            from app.providers.aws.cost_explorer import CostExplorerAdapter

            db = SessionLocal()
            try:
                acct = db.query(CloudAccountDB).filter(
                    CloudAccountDB.provider == "AWS"
                ).first()
                account_id = acct.id if acct else 1
            finally:
                db.close()

            adapter = CostExplorerAdapter(account_id)

            current_month  = 0.0
            previous_month = 0.0
            daily_breakdown: List[Dict] = []

            try:
                current_month = adapter.get_current_month_cost()
            except Exception as exc:
                logger.debug("CostProvider current_month error: %s", exc)

            try:
                trend = adapter.get_daily_cost_trend(days=60)
                if trend:
                    mid = len(trend) // 2
                    # Last 30 days = current period
                    daily_breakdown = trend[mid:]
                    # First 30 days = previous period
                    prev = trend[:mid]
                    previous_month = round(sum(p["amount"] for p in prev), 2)
            except Exception as exc:
                logger.debug("CostProvider daily_trend error: %s", exc)

            avg_daily = 0.0
            if daily_breakdown:
                avg_daily = round(
                    sum(p.get("amount", 0.0) for p in daily_breakdown) / len(daily_breakdown),
                    4
                )

            is_idle              = avg_daily < IDLE_THRESHOLD_USD_PER_DAY
            potential_savings    = round(avg_daily * 30 * 0.3, 2) if is_idle else 0.0  # 30% saving

            return {
                "currency":              "USD",
                "granularity":           granularity,
                "current_month_usd":     current_month,
                "previous_month_usd":    previous_month,
                "avg_30d_daily_usd":     avg_daily,
                "is_idle":               is_idle,
                "potential_savings_usd": potential_savings,
                "daily_breakdown":       daily_breakdown,
            }

        except Exception as exc:
            logger.warning("CostProvider failed for %s: %s", resource_id, exc)
            return self._empty(resource_id)

    def _empty(self, resource_id: str) -> Dict[str, Any]:
        return {
            "currency":              "USD",
            "granularity":           "daily",
            "current_month_usd":     0.0,
            "previous_month_usd":    0.0,
            "avg_30d_daily_usd":     0.0,
            "is_idle":               False,
            "potential_savings_usd": 0.0,
            "daily_breakdown":       [],
        }
