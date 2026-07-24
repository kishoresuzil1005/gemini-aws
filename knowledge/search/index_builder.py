# knowledge/search/index_builder.py
"""Builds the search index from the Knowledge Platform catalogs.

The builder pulls data from the existing Knowledge Service catalogs using the
public `list_*` methods (which return raw model objects).  It then transforms
each entity into a flat document suitable for the SQLite FTS5 backend defined
in ``search_index.py``.

Only read‑only operations are performed – the underlying catalogs are never
modified, satisfying the project constraints.
"""

from typing import Iterable, Dict, Any

from .search_index import get_index

class IndexBuilder:
    """Collects data from the platform and populates the FTS5 index.

    Parameters
    ----------
    resource_catalog, relationship_catalog, rule_catalog, documentation_provider
        Instances that expose a ``list_*`` method returning iterable model objects.
    """

    def __init__(self, resource_catalog, relationship_catalog, rule_catalog, documentation_provider=None):
        self.resource_catalog = resource_catalog
        self.relationship_catalog = relationship_catalog
        self.rule_catalog = rule_catalog
        self.documentation_provider = documentation_provider
        self.index = get_index()

    # -----------------------------------------------------------------
    # Helper: Transform a model instance into a flat dictionary for the index
    # -----------------------------------------------------------------
    def _doc_from_resource(self, res) -> Dict[str, Any]:
        return {
            "id": getattr(res, "resource_id", ""),
            "type": "resource",
            "name": getattr(res, "canonical_name", ""),
            "description": getattr(res, "description", ""),
            "tags": getattr(res, "tags", []),
            "content": getattr(res, "metadata", {}),
        }

    def _doc_from_relationship(self, rel) -> Dict[str, Any]:
        return {
            "id": getattr(rel, "relationship_id", ""),
            "type": "relationship",
            "name": getattr(rel, "name", ""),
            "description": getattr(rel, "description", ""),
            "tags": getattr(rel, "tags", []),
            "content": getattr(rel, "metadata", {}),
        }

    def _doc_from_rule(self, rule) -> Dict[str, Any]:
        return {
            "id": getattr(rule, "rule_id", ""),
            "type": "rule",
            "name": getattr(rule, "canonical_name", ""),
            "description": getattr(rule, "description", ""),
            "tags": getattr(rule, "tags", []),
            "content": getattr(rule, "metadata", {}),
        }

    # -----------------------------------------------------------------
    # Public build entry point
    # -----------------------------------------------------------------
    def build(self, clear_existing: bool = True) -> None:
        """Re‑creates the entire index.

        If ``clear_existing`` is ``True`` the previous index tables are emptied
        before new documents are inserted.
        """
        if clear_existing:
            self.index.clear()

        # Resources
        for res in self.resource_catalog.list_resources():
            self.index.add_document("resources", self._doc_from_resource(res))

        # Relationships
        for rel in self.relationship_catalog.list_relationships():
            self.index.add_document("relationships", self._doc_from_relationship(rel))

        # Rules
        for rule in self.rule_catalog.list_rules():
            self.index.add_document("rules", self._doc_from_rule(rule))

        # Documentation – optional, placeholder for future extension
        if self.documentation_provider and hasattr(self.documentation_provider, "list_documents"):
            for doc in self.documentation_provider.list_documents():
                # Expected doc to have id, title, content, tags attributes
                self.index.add_document(
                    "documents",
                    {
                        "id": getattr(doc, "doc_id", ""),
                        "type": "document",
                        "name": getattr(doc, "title", ""),
                        "description": getattr(doc, "summary", ""),
                        "tags": getattr(doc, "tags", []),
                        "content": getattr(doc, "content", {}),
                    },
                )
