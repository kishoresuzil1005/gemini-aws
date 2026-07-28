# knowledge/search/search_index.py
"""Low‑level SQLite FTS5 index wrapper.

This implementation stores searchable documents for the four core entity types
(resources, relationships, rules, documentation).  Each type gets its own FTS5
virtual table with the same set of columns so that the higher‑level search code
can treat them uniformly.

The index is persisted under ``.search_index/search.db`` inside the workspace
so that it survives process restarts.  Compression and deduplication are
handled at a higher level (snapshot & version management) – the index itself
focuses on fast full‑text lookup.
"""

import os
import sqlite3
from typing import List, Dict, Any

INDEX_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".search_index"))
DB_PATH = os.path.join(INDEX_DIR, "search.db")

class SearchIndex:
    """SQLite FTS5 based index.

    The schema for each entity is::

        CREATE VIRTUAL TABLE IF NOT EXISTS {table} USING fts5(
            id UNINDEXED,
            type UNINDEXED,
            name,
            description,
            tags,
            content
        );

    ``name`` and ``description`` are the primary full‑text fields, ``tags``
    stores a space‑separated list of tags, and ``content`` can hold any extra
    searchable text (e.g., aliases, provider name, etc.).
    """

    def __init__(self):
        os.makedirs(INDEX_DIR, exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH)
        self._ensure_tables()
        self.conn.row_factory = sqlite3.Row

    def _ensure_tables(self) -> None:
        cursor = self.conn.cursor()
        tables = ["resources", "relationships", "rules", "documents", "snapshots", "versions"]
        for tbl in tables:
            cursor.execute(
                f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS {tbl} USING fts5(
                    id UNINDEXED,
                    type UNINDEXED,
                    name,
                    description,
                    tags,
                    content
                );
                """
            )
        self.conn.commit()

    def clear(self) -> None:
        """Delete all rows from every FTS5 table (used for full rebuild)."""
        cursor = self.conn.cursor()
        for tbl in ["resources", "relationships", "rules", "documents", "snapshots", "versions"]:
            cursor.execute(f"DELETE FROM {tbl};")
        self.conn.commit()

    def add_document(self, table: str, doc: Dict[str, Any]) -> None:
        """Insert a single document into the specified FTS5 table.

        Parameters
        ----------
        table: str
            One of the known tables (resources, relationships, rules, …).
        doc: dict
            Keys required: ``id``, ``type``, ``name``, ``description``, ``tags``,
            ``content``. Missing optional fields are stored as empty strings.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            f"INSERT INTO {table} (id, type, name, description, tags, content) VALUES (?,?,?,?,?,?)",
            (
                doc.get("id", ""),
                doc.get("type", ""),
                doc.get("name", ""),
                doc.get("description", ""),
                " ".join(doc.get("tags", [])),
                doc.get("content", ""),
            ),
        )
        self.conn.commit()

    def delete_document(self, table: str, doc_id: str) -> None:
        cursor = self.conn.cursor()
        cursor.execute(f"DELETE FROM {table} WHERE id = ?", (doc_id,))
        self.conn.commit()

    def search(self, table: str, term: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Perform a simple full‑text search on *term* within *table*.

        The term is passed directly to the FTS5 ``MATCH`` operator, which
        supports prefix, wildcard, and fuzzy syntax out of the box.
        """
        cursor = self.conn.cursor()
        query = f"SELECT id, type, name, description, tags, content FROM {table} WHERE {table} MATCH ? LIMIT ? OFFSET ?"
        cursor.execute(query, (term, limit, offset))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def close(self) -> None:
        self.conn.close()

# Helper instance used by the manager (singleton pattern for simplicity)
_index_instance: SearchIndex | None = None

def get_index() -> SearchIndex:
    global _index_instance
    if _index_instance is None:
        _index_instance = SearchIndex()
    return _index_instance
