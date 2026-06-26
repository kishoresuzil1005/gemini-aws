import logging

from app.services.diagram.icon_assets import IconAssetManager
from app.services.diagram.svg_icon_loader import SVGLoader
from app.services.diagram.svg_sanitizer import SVGSanitizer

logger = logging.getLogger("SVGIconCache")


class SVGIconCache:
    """
    In-memory cache for sanitized AWS SVG icons.

    Responsibilities
    ----------------
    - Load icon once
    - Sanitize once
    - Cache forever
    """

    _cache: dict[str, str] = {}

    @classmethod
    def get(cls, resource_type: str) -> str | None:
        """
        Return sanitized SVG for a resource.

        Returns None if the icon cannot be loaded.
        """

        if not resource_type:
            return None

        if resource_type in cls._cache:
            return cls._cache[resource_type]

        icon_path = IconAssetManager.get_icon_path(resource_type)

        if not icon_path:
            logger.warning(
                "No icon registered for %s",
                resource_type
            )
            return None

        raw_svg = SVGLoader.load(icon_path)

        if raw_svg is None:
            return None

        clean_svg = SVGSanitizer.sanitize(raw_svg)

        cls._cache[resource_type] = clean_svg

        return clean_svg

    @classmethod
    def clear(cls):
        """
        Clear cache.
        Useful during development.
        """
        cls._cache.clear()

    @classmethod
    def size(cls):
        """
        Number of cached icons.
        """
        return len(cls._cache)

    @classmethod
    def keys(cls):
        """
        Cached resource types.
        """
        return sorted(cls._cache.keys())
