"""
Prompt Budget Manager (Phase 10)
==================================
Estimates token counts per context section and truncates / summarises
lower-priority sections when the total exceeds the configured budget.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)

# Rough token estimator: ~4 chars per token for English text
_CHARS_PER_TOKEN = 4

# Default maximum tokens for the final prompt payload
DEFAULT_BUDGET = 3000

# Priority order for truncation (last items get truncated first)
_SECTION_PRIORITY: List[str] = [
    "resource",
    "security",
    "graph",
    "metrics",
    "cost",
    "documentation",
    "raw",
]


def _estimate_tokens(obj: Any) -> int:
    """Estimate token count from any serialisable object."""
    try:
        text = json.dumps(obj, default=str)
    except Exception:
        text = str(obj)
    return max(1, len(text) // _CHARS_PER_TOKEN)


class BudgetManager:
    """Enforces a prompt token budget across context sections."""

    def __init__(self, budget: int = DEFAULT_BUDGET):
        self.budget = budget

    def enforce(self, sections: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Given a dict of {section_name: data}, return a pruned dict that fits
        within the token budget and a list of sections that were truncated.

        Args:
            sections: ordered dict of context sections.
        Returns:
            (pruned_sections, truncated_section_names)
        """
        total = sum(_estimate_tokens(v) for v in sections.values())
        if total <= self.budget:
            logger.debug("[BudgetManager] Within budget: %d / %d tokens", total, self.budget)
            return sections, []

        logger.warning(
            "[BudgetManager] Over budget: %d tokens > %d limit — pruning…", total, self.budget
        )

        pruned = dict(sections)
        truncated: List[str] = []

        # Truncate from lowest priority sections first
        for section in reversed(_SECTION_PRIORITY):
            if total <= self.budget:
                break
            if section not in pruned:
                continue
            excess = total - self.budget
            section_tokens = _estimate_tokens(pruned[section])
            if section_tokens <= excess:
                # Drop entire section
                del pruned[section]
                total -= section_tokens
                truncated.append(section)
                logger.warning("[BudgetManager] Dropped section '%s' (%d tokens)", section, section_tokens)
            else:
                # Partially truncate (summarise as a string)
                summary = f"[truncated — section too large ({section_tokens} tokens)]"
                pruned[section] = summary
                total = total - section_tokens + _estimate_tokens(summary)
                truncated.append(section)
                logger.warning("[BudgetManager] Truncated section '%s'", section)

        logger.info(
            "[BudgetManager] Final token estimate: %d / %d | truncated: %s",
            total,
            self.budget,
            truncated,
        )
        return pruned, truncated
