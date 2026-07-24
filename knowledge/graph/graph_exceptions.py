# knowledge/graph/graph_exceptions.py
"""Custom exceptions for the Knowledge Graph."""

class GraphError(Exception):
    """Base exception for Graph operations."""
    pass

class NodeNotFoundError(GraphError):
    """Raised when querying a node that does not exist in the graph."""
    pass

class EdgeNotFoundError(GraphError):
    """Raised when querying an edge that does not exist in the graph."""
    pass

class DisconnectedGraphError(GraphError):
    """Raised when a traversal encounters an unexpectedly disconnected component."""
    pass
