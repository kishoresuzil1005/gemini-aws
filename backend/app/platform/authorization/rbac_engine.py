from enum import Enum
from typing import List, Dict, Any

class Role(str, Enum):
    ADMIN = "ADMIN"
    ENGINEER = "ENGINEER"
    VIEWER = "VIEWER"
    SECURITY = "SECURITY"
    FINANCE = "FINANCE"

class RBACEngine:
    """
    Role-Based Access Control evaluator for enterprise platforms.
    """
    def __init__(self):
        self.role_permissions = {
            Role.ADMIN: ["*"],
            Role.ENGINEER: ["read:*", "write:mission", "execute:workflow"],
            Role.VIEWER: ["read:*"],
            Role.SECURITY: ["read:*", "write:policy", "execute:audit"],
            Role.FINANCE: ["read:billing", "read:cost", "write:budget"]
        }

    def check_permission(self, role: Role, required_permission: str) -> bool:
        allowed_perms = self.role_permissions.get(role, [])
        if "*" in allowed_perms:
            return True
        for p in allowed_perms:
            if required_permission.startswith(p.replace("*", "")):
                return True
        return False
