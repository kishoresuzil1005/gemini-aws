# knowledge/service/lifecycle.py
"""Lifecycle interface for Knowledge Platform runtime services."""

class Lifecycle:
    """Base lifecycle class for services."""
    def initialize(self) -> None:
        ...
        
    def start(self) -> None:
        ...
        
    def ready(self) -> bool:
        return True
        
    def shutdown(self) -> None:
        ...
        
    def dispose(self) -> None:
        ...
        
    def restart(self) -> None:
        self.shutdown()
        self.dispose()
        self.initialize()
        self.start()
