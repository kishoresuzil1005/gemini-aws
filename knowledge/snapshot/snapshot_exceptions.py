# knowledge/snapshot/snapshot_exceptions.py
"""Custom exceptions for the Snapshot Engine."""

class SnapshotError(Exception):
    """Base exception for Snapshot operations."""
    pass

class IntegrityError(SnapshotError):
    """Raised when a snapshot fails a checksum or manifest validation."""
    pass

class RollbackError(SnapshotError):
    """Raised when a rollback operation fails or is aborted."""
    pass
