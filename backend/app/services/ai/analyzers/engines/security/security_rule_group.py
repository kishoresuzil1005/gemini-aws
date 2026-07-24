"""
Security Rule Group Provider.
"""
from abc import ABC, abstractmethod
from typing import List
from app.services.ai.analyzers.engines.security.security_rule import SecurityRule

class SecurityRuleGroup(ABC):
    """
    A lightweight container that groups related security rules (e.g. all IAM rules).
    It is NOT a rule itself. Its sole responsibility is to provide a list of initialized
    SecurityRule instances to the SecurityRegistry.
    """
    
    @abstractmethod
    def rules(self) -> List[SecurityRule]:
        """Returns all rules managed by this group."""
        pass
