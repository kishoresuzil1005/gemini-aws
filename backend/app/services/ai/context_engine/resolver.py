"""ResourceResolver – resolves any user-supplied identifier to a fully-populated
``ResolvedResource`` by searching the PostgreSQL inventory.

Resolution order
----------------
1. Exact match on ``resources.resource_id``      (e.g. "i-0abc123", "db-xxxx")
2. Case-insensitive match on ``resources.name``  (e.g. "cloudops-db")
3. Partial / ILIKE match on ``resources.name``   (e.g. "cloudops")
4. Fallback: return a stub so the pipeline can still attempt Neo4j queries.
"""

import json
import logging
from typing import Optional

from app.database import SessionLocal

from .request import ContextRequest
from .resolved_resource import ResolvedResource
from .exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)


class ResourceResolver:
    """Resolves any identifier → canonical ``ResolvedResource``."""

    async def resolve_identifier(self, request: ContextRequest) -> ResolvedResource:
        identifier = (request.identifier or "").strip()
        if not identifier:
            raise ResourceNotFoundError("Identifier cannot be empty")

        resolved = self._lookup(identifier)
        if resolved:
            logger.info(
                "ResourceResolver: '%s' → %s (%s)",
                identifier,
                resolved.resource_id,
                resolved.resource_type,
            )
            return resolved

        # Nothing found – return a stub so downstream providers can still try
        logger.warning(
            "ResourceResolver: no DB match for '%s'; using stub", identifier
        )
        return ResolvedResource(
            resource_id=identifier,
            original_identifier=identifier,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _lookup(self, identifier: str) -> Optional[ResolvedResource]:
        """Try each resolution strategy in order and return on first hit."""
        db = SessionLocal()
        try:
            from app.models import ResourceDB  # local import avoids circular deps

            # 1. Exact resource_id match
            row = (
                db.query(ResourceDB)
                .filter(ResourceDB.resource_id == identifier)
                .first()
            )

            # 2. Exact name match (case-insensitive)
            if row is None:
                row = (
                    db.query(ResourceDB)
                    .filter(ResourceDB.name.ilike(identifier))
                    .first()
                )

            # 3. Partial name match (prefix / substring)
            if row is None:
                row = (
                    db.query(ResourceDB)
                    .filter(ResourceDB.name.ilike(f"%{identifier}%"))
                    .first()
                )

            if row is None:
                return None

            return self._row_to_resolved(row, identifier)

        except Exception as exc:
            logger.warning("ResourceResolver DB error: %s", exc)
            return None
        finally:
            db.close()

    @staticmethod
    def _row_to_resolved(row, original_identifier: str) -> ResolvedResource:
        """Convert a ``ResourceDB`` row into a ``ResolvedResource``."""
        tags: dict = {}
        if row.tags:
            try:
                tags = json.loads(row.tags)
            except Exception:
                pass

        meta: dict = {}
        if row.resource_metadata:
            meta = row.resource_metadata if isinstance(row.resource_metadata, dict) else {}

        arn = meta.get("arn", "") if meta else ""

        return ResolvedResource(
            resource_id=row.resource_id,
            original_identifier=original_identifier,
            resource_name=row.name or row.resource_id,
            resource_type=row.resource_type,
            provider=row.provider or "aws",
            region=row.region or "",
            account_id=str(row.cloud_account_id or ""),
            arn=arn,
            status=row.status or "unknown",
            tags=tags,
            metadata=meta,
        )
