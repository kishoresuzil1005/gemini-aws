# knowledge/snapshot/snapshot_exceptions.py
"""Custom exceptions for the Snapshot Engine."""

class SnapshotError(Exception):
    """Base exception for Snapshot operations."""
    ...

class IntegrityError(SnapshotError):
    """Raised when a snapshot fails a checksum or manifest validation."""
    ...

class RollbackError(SnapshotError):
    """Raised when a rollback operation fails or is aborted."""
    ...
