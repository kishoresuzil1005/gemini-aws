"""
Security Rule Registry.
Responsible for storing and filtering immutable rules with advanced indexing.
Implements auto-discovery of RuleGroups via importlib.
"""
import logging
import importlib
import pkgutil
import inspect
from typing import List, Dict, Type, Any, Optional
from app.services.ai.analyzers.engines.security.security_rule import SecurityRule
from app.services.ai.analyzers.engines.security.security_rule_group import SecurityRuleGroup
from app.services.ai.analyzers.base.analyzer_models import SupportedResource, CloudProvider
from app.services.ai.analyzers.engines.security.security_models import SecurityDomain, SecurityCategory, RuleStatus

logger = logging.getLogger(__name__)

class SecurityRuleRegistry:
    def __init__(self):
        self._rules: Dict[str, SecurityRule] = {}
        
        # Advanced Indices
        self._domain_index: Dict[SecurityDomain, List[str]] = {}
        self._category_index: Dict[SecurityCategory, List[str]] = {}
        self._severity_index: Dict[str, List[str]] = {}
        self._status_index: Dict[RuleStatus, List[str]] = {}
        self._tag_index: Dict[str, List[str]] = {}
        self._provider_index: Dict[CloudProvider, List[str]] = {}
        self._resource_index: Dict[str, List[str]] = {}
        
    def register(self, rule: SecurityRule):
        meta = rule.metadata()
        rule_id = meta.id
        
        if rule_id in self._rules:
            logger.warning(f"Rule {rule_id} is already registered. Use replace() to update it.")
            return
            
        self._rules[rule_id] = rule
        
        # Build indices
        self._domain_index.setdefault(meta.domain, []).append(rule_id)
        self._category_index.setdefault(meta.category, []).append(rule_id)
        self._provider_index.setdefault(meta.provider, []).append(rule_id)
        
        sev_str = meta.severity.value if hasattr(meta.severity, 'value') else str(meta.severity)
        self._severity_index.setdefault(sev_str, []).append(rule_id)
        
        self._status_index.setdefault(meta.status, []).append(rule_id)
        
        for tag in meta.tags:
            self._tag_index.setdefault(tag, []).append(rule_id)
            
        for r_type in meta.resource_types:
            self._resource_index.setdefault(r_type, []).append(rule_id)
            
    def register_group(self, group: SecurityRuleGroup):
        """Unpacks a RuleGroup and registers each rule individually."""
        for rule in group.rules():
            self.register(rule)
            
    def discover(self, package_path: str = "app.services.ai.analyzers.engines.security.rules"):
        """Automatically discovers and registers RuleGroups using importlib."""
        logger.info(f"Starting automatic rule discovery in {package_path}...")
        try:
            package = importlib.import_module(package_path)
        except ImportError as e:
            logger.error(f"Failed to import rule package {package_path}: {e}")
            return
            
        # Recursive walk
        for _, module_name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
            try:
                module = importlib.import_module(module_name)
                # Find all classes that inherit from SecurityRuleGroup
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, SecurityRuleGroup) and obj is not SecurityRuleGroup:
                        if not inspect.isabstract(obj):
                            # Instantiate the group and register its rules
                            group_instance = obj()
                            self.register_group(group_instance)
                            logger.info(f"Registered RuleGroup: {name}")
            except Exception as e:
                logger.error(f"Error loading rules from {module_name}: {e}")
            
    def unregister(self, rule_id: str):
        if rule_id in self._rules:
            del self._rules[rule_id]
            
    def replace(self, rule: SecurityRule):
        self.unregister(rule.metadata().id)
        self.register(rule)
        
    def enable_rule(self, rule_id: str):
        pass # Stub
        
    def disable_rule(self, rule_id: str):
        pass # Stub
        
    def reload(self):
        self._rules.clear()
        self.discover()
        
    # Standard APIs
    def get_rule(self, rule_id: str) -> Optional[SecurityRule]:
        return self._rules.get(rule_id)
        
    def list_rules(self) -> List[SecurityRule]:
        return list(self._rules.values())
        
    def list_domains(self) -> List[SecurityDomain]:
        return list(self._domain_index.keys())
        
    def list_categories(self) -> List[SecurityCategory]:
        return list(self._category_index.keys())
        
    def list_by_provider(self, provider: CloudProvider) -> List[SecurityRule]:
        return [self._rules[rid] for rid in self._provider_index.get(provider, []) if rid in self._rules]
        
    def list_by_resource(self, resource_type: str) -> List[SecurityRule]:
        return [self._rules[rid] for rid in self._resource_index.get(resource_type, []) if rid in self._rules]
        
    def list_by_tag(self, tag: str) -> List[SecurityRule]:
        return [self._rules[rid] for rid in self._tag_index.get(tag, []) if rid in self._rules]
        
    def statistics(self) -> Dict[str, Any]:
        return {
            "total_rules": len(self._rules),
            "by_domain": {k.value: len(v) for k, v in self._domain_index.items()},
            "by_category": {k.value: len(v) for k, v in self._category_index.items()},
            "by_severity": {k: len(v) for k, v in self._severity_index.items()}
        }
        
    def get_rules_for_node(self, node_type: str) -> List[SecurityRule]:
        """Returns all rules that explicitly support the given node type."""
        active_rules = []
        enabled_ids = set(self._status_index.get(RuleStatus.ENABLED, []))
        audit_ids = set(self._status_index.get(RuleStatus.AUDIT_ONLY, []))
        
        for rule_id in (enabled_ids | audit_ids):
            rule = self._rules.get(rule_id)
            if rule and rule.supports(node_type):
                active_rules.append(rule)
                
        return active_rules
