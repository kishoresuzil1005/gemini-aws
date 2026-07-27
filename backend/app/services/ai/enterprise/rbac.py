"""RBAC-Aware AI — Phase 4"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class AIPermissions:
    user_id: str
    roles: List[str] = field(default_factory=list)
    allowed_actions: List[str] = field(default_factory=list)
    denied_resources: List[str] = field(default_factory=list)
    require_approval_for: List[str] = field(default_factory=list)

    def can(self, action: str) -> bool:
        if action in self.denied_resources:
            return False
        return "admin" in self.roles or action in self.allowed_actions

    def needs_approval(self, action: str) -> bool:
        return action in self.require_approval_for
