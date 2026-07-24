# knowledge/search/index_validator.py
"""Validates the integrity of the SQLite FTS5 index.

The validator checks that each expected virtual table exists and that the
record count matches a simple checksum (row count) stored in a manifest file.
For this baseline implementation we only verify table presence and that no
duplicate ``id`` values exist within a table.
"""

import os
import sqlite3
from typing import List

from .search_index import INDEX_DIR, DB_PATH

class IndexValidator:
    """Performs sanity checks on the search index.

    Methods raise ``ValueError`` with a descriptive message when a problem is
    detected.  Consumers can catch the exception and surface it via the public
    ``search_engine`` API.
    """

    EXPECTED_TABLES = ["resources", "relationships", "rules", "documents", "snapshots", "versions"]

    def __init__(self):
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError(f"Search index database not found at {DB_PATH}")
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row

    def _check_tables_exist(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing = {row["name"] for row in cursor.fetchall()}
        missing = set(self.EXPECTED_TABLES) - existing
        if missing:
            raise ValueError(f"Missing expected FTS5 tables: {', '.join(missing)}")

    def _check_duplicate_ids(self) -> None:
        cursor = self.conn.cursor()
        for table in self.EXPECTED_TABLES:
            cursor.execute(f"SELECT id, COUNT(*) as cnt FROM {table} GROUP BY id HAVING cnt > 1;")
            duplicates = cursor.fetchall()
            if duplicates:
                dup_ids = [row["id"] for row in duplicates]
                raise ValueError(f"Duplicate IDs found in table '{table}': {', '.join(dup_ids)}")

    def validate(self) -> None:
        """Run all validation steps. Raises ``ValueError`` on failure."""
        self._check_tables_exist()
        self._check_duplicate_ids()
        # Additional checks (e.g., checksum verification) could be added here.

    def close(self) -> None:
        self.conn.close()
