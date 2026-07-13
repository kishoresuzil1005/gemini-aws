from abc import ABC, abstractmethod

class DiscoveryScheduler(ABC):
    """Base interface for queueing and scheduling discovery jobs."""
    @abstractmethod
    def schedule_full_discovery(self, provider: str):
        pass

    @abstractmethod
    def schedule_incremental_discovery(self, provider: str, region: str):
        pass
