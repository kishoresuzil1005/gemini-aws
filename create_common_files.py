import os

COMMON_DIR = "backend/app/providers/common"
os.makedirs(COMMON_DIR, exist_ok=True)

files = {
    "client_factory.py": """
from typing import Dict, Any, Optional
import boto3

class ClientFactory:
    \"\"\"Central factory for generating all SDK clients (boto3, azure, gcp, kubernetes).\"\"\"
    def __init__(self):
        self._clients: Dict[str, Any] = {}

    def get_aws_client(self, service_name: str, region_name: Optional[str] = None, credentials: Optional[Dict] = None) -> Any:
        cache_key = f"aws_{service_name}_{region_name}"
        if cache_key not in self._clients:
            kwargs = {'region_name': region_name} if region_name else {}
            if credentials:
                kwargs.update(credentials)
            self._clients[cache_key] = boto3.client(service_name, **kwargs)
        return self._clients[cache_key]

    # Additional methods for Azure, GCP, K8s would go here...
    def get_azure_client(self, client_class: Any, credentials: Any, **kwargs) -> Any:
        pass
    
    def get_gcp_client(self, client_class: Any, credentials: Any, **kwargs) -> Any:
        pass
    
    def get_kubernetes_client(self, client_class: Any, **kwargs) -> Any:
        pass

client_factory = ClientFactory()
""",
    "credential_manager.py": """
from typing import Dict, Any, Optional

class CredentialManager:
    \"\"\"Resolves credentials across all providers.\"\"\"
    def get_aws_credentials(self, account_id: Optional[str] = None, role_arn: Optional[str] = None) -> Dict[str, str]:
        # Return resolved credentials for AWS (STS AssumeRole, local, etc)
        return {}

    def get_azure_credentials(self):
        # Return AzureDefaultCredential etc.
        pass

    def get_gcp_credentials(self):
        # Return GCP Service Account credentials
        pass

    def get_kubernetes_credentials(self):
        # Return kubeconfig or incluster config
        pass
""",
    "region_manager.py": """
from typing import List, Optional

class RegionManager:
    \"\"\"Centralizes region handling across all clouds.\"\"\"
    def __init__(self):
        self._default_aws_region = "us-east-1"
        self._default_azure_region = "eastus"
        self._default_gcp_region = "us-central1"

    def get_active_regions(self, provider: str) -> List[str]:
        if provider == "aws":
            return [self._default_aws_region]
        return []

    def get_default_region(self, provider: str) -> str:
        if provider == "aws": return self._default_aws_region
        elif provider == "azure": return self._default_azure_region
        elif provider == "gcp": return self._default_gcp_region
        return "global"
""",
    "inventory_diff.py": """
from typing import List, Dict, Any, Tuple

class InventoryDiffEngine:
    \"\"\"
    Calculates differences between existing inventory and new discovery runs.
    Prevents replacing the entire graph/database on each run.
    \"\"\"
    def calculate_diff(self, old_inventory: List[Dict[str, Any]], new_inventory: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        old_map = {res['resource_id']: res for res in old_inventory if 'resource_id' in res}
        new_map = {res['resource_id']: res for res in new_inventory if 'resource_id' in res}

        added = []
        removed = []
        changed = []

        for r_id, r_data in new_map.items():
            if r_id not in old_map:
                added.append(r_data)
            elif old_map[r_id] != r_data:
                changed.append(r_data)

        for r_id, r_data in old_map.items():
            if r_id not in new_map:
                removed.append(r_data)

        return {
            "added": added,
            "removed": removed,
            "changed": changed
        }
""",
    "provider_events.py": """
from typing import Dict, Any

class ProviderEventBus:
    \"\"\"Publishes events emitted by the provider layer to the platform.\"\"\"
    def publish(self, event_type: str, payload: Dict[str, Any]):
        # e.g., send to Kafka, Redis PubSub, or in-memory queue
        print(f"[EVENT] {event_type}: {payload}")

provider_event_bus = ProviderEventBus()
""",
    "provider_logger.py": """
import logging

def get_provider_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(f"provider.{name}")
    if not logger.handlers:
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.setLevel(logging.INFO)
    return logger
""",
    "provider_context.py": """
import uuid
from typing import Dict, Any

class ProviderContext:
    \"\"\"Passes context (request ID, timeout, etc.) down through provider calls.\"\"\"
    def __init__(self, request_id: str = None, timeout: int = 30):
        self.request_id = request_id or str(uuid.uuid4())
        self.timeout = timeout
        self.state: Dict[str, Any] = {}
""",
    "provider_cache_manager.py": """
from typing import Dict, Any, Optional
import time

class ProviderCacheManager:
    \"\"\"Manages caching of provider responses and metrics.\"\"\"
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if entry and time.time() < entry['expiry']:
            return entry['value']
        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        self._cache[key] = {
            'value': value,
            'expiry': time.time() + ttl_seconds
        }
""",
    "discovery_scheduler.py": """
from abc import ABC, abstractmethod

class DiscoveryScheduler(ABC):
    \"\"\"Base interface for queueing and scheduling discovery jobs.\"\"\"
    @abstractmethod
    def schedule_full_discovery(self, provider: str):
        pass

    @abstractmethod
    def schedule_incremental_discovery(self, provider: str, region: str):
        pass
""",
    "retry_engine.py": """
import time
import logging
from typing import Callable, Any
from enum import Enum

logger = logging.getLogger(__name__)

class RetryProfile(Enum):
    FAST = (3, 1.0)
    CRITICAL = (5, 2.0)
    DISCOVERY = (10, 5.0)
    BACKGROUND = (3, 10.0)

class RetryEngine:
    \"\"\"Provides exponential backoff retries with specific profiles.\"\"\"
    @staticmethod
    def execute_with_retry(func: Callable, profile: RetryProfile = RetryProfile.FAST, *args, **kwargs) -> Any:
        max_retries, backoff = profile.value
        attempt = 0
        while attempt < max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                attempt += 1
                logger.warning(f"Attempt {attempt}/{max_retries} failed: {str(e)}")
                if attempt >= max_retries:
                    raise
                time.sleep(backoff ** attempt)
""",
    "rate_limiter.py": """
import time

class RateLimiter:
    \"\"\"Simple token bucket or sleep-based rate limiting to avoid provider throttling.\"\"\"
    def __init__(self, calls_per_second: float):
        self.interval = 1.0 / calls_per_second
        self.last_call = 0.0

    def wait(self):
        now = time.time()
        elapsed = now - self.last_call
        if elapsed < self.interval:
            time.sleep(self.interval - elapsed)
        self.last_call = time.time()
""",
    "pagination_helper.py": """
from typing import Callable, List, Dict, Any, Optional

class PaginationHelper:
    \"\"\"Abstracts cloud API pagination loops (NextToken, next_page_token, etc.).\"\"\"
    @staticmethod
    def paginate(
        func: Callable, 
        items_key: str, 
        token_key: str = 'NextToken', 
        req_token_key: str = 'NextToken',
        **kwargs
    ) -> List[Dict[str, Any]]:
        results = []
        token: Optional[str] = None
        
        while True:
            if token:
                kwargs[req_token_key] = token
            response = func(**kwargs)
            
            items = response.get(items_key, [])
            results.extend(items)
            
            token = response.get(token_key)
            if not token:
                break
                
        return results
""",
    "operation_tracker.py": """
from typing import Any

class OperationTracker:
    \"\"\"Tracks Long Running Operations (LRO).\"\"\"
    def __init__(self):
        self.operations = {}

    def track(self, operation_id: str, status: str):
        self.operations[operation_id] = status

    def get_status(self, operation_id: str) -> str:
        return self.operations.get(operation_id, "UNKNOWN")
""",
    "circuit_breaker.py": """
import time

class CircuitBreaker:
    \"\"\"Prevents cascading failures by short-circuiting calls if error threshold is reached.\"\"\"
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = 0
        self.is_open = False

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.is_open = True

    def record_success(self):
        self.failures = 0
        self.is_open = False

    def can_execute(self) -> bool:
        if not self.is_open:
            return True
        if time.time() - self.last_failure_time > self.recovery_timeout:
            # Half-open state
            return True
        return False
""",
    "timeout_manager.py": """
import signal
from contextlib import contextmanager
from app.providers.common.errors import TimeoutError

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutError("Timed out!")
    
    # This only works on UNIX/Linux
    try:
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(seconds)
        yield
    finally:
        try:
            signal.alarm(0)
        except Exception:
            pass
"""
}

for filename, content in files.items():
    filepath = os.path.join(COMMON_DIR, filename)
    with open(filepath, 'w') as f:
        f.write(content.strip() + "\\n")
    print(f"Created {filepath}")
