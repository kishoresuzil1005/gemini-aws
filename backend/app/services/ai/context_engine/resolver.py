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
            
    def find_candidates(self, resource_ids: list[str], keywords: list[str], tag_filters: dict[str, str] = None) -> list[dict]:
        """Search PostgreSQL inventory for candidates based on IDs, names, types, or tags."""
        db = SessionLocal()
        candidates = []
        try:
            from app.models import ResourceDB
            
            # Combine all search terms for flexible matching
            search_terms = resource_ids + keywords
            if not search_terms and not tag_filters:
                return candidates
                
            seen_ids = set()
            
            # 1. Check exact IDs
            if resource_ids:
                rows = db.query(ResourceDB).filter(ResourceDB.resource_id.in_(resource_ids)).all()
                for row in rows:
                    if row.resource_id not in seen_ids:
                        candidates.append(self._row_to_dict(row, "postgres"))
                        seen_ids.add(row.resource_id)
            
            # 2. Check Tag filters if provided
            if tag_filters:
                # Basic JSONB contains check (assumes tags is a JSON string or JSONB)
                for tag_key, tag_val in tag_filters.items():
                    # For text field, we just do a string contains
                    rows = db.query(ResourceDB).filter(ResourceDB.tags.ilike(f"%\"{tag_key}\":%\"{tag_val}\"%")).limit(10).all()
                    for row in rows:
                        if row.resource_id not in seen_ids:
                            candidates.append(self._row_to_dict(row, "tag_store"))
                            seen_ids.add(row.resource_id)
                            
            # 3. Check Names and Types (Keywords)
            if keywords:
                for kw in keywords:
                    rows = db.query(ResourceDB).filter(
                        (ResourceDB.name.ilike(kw)) | 
                        (ResourceDB.resource_type.ilike(kw))
                    ).limit(10).all()
                    for row in rows:
                        if row.resource_id not in seen_ids:
                            candidates.append(self._row_to_dict(row, "postgres"))
                            seen_ids.add(row.resource_id)
                            
            return candidates
        except Exception as exc:
            logger.warning("ResourceResolver DB error in find_candidates: %s", exc)
            return candidates
        finally:
            db.close()
            
    @staticmethod
    def _row_to_dict(row, source: str) -> dict:
        meta = row.resource_metadata if isinstance(row.resource_metadata, dict) else {}
        arn = meta.get("arn", "") if meta else ""
        return {
            "id": row.resource_id,
            "arn": arn,
            "name": row.name or row.resource_id,
            "type": [row.resource_type] if row.resource_type else [],
            "region": row.region,
            "account": str(row.cloud_account_id or ""),
            "source": source
        }

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
