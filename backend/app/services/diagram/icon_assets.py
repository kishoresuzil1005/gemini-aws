from pathlib import Path
from functools import lru_cache
import re
import logging

logger = logging.getLogger("IconAssetManager")


class IconAssetManager:
    """
    Resolves AWS SVG icon locations.

    This is the single source of truth for icon assets.
    Auto-indexes the assets folder at startup to gracefully support newer icon packs.
    """

    BASE_DIR = (
        Path(__file__)
        .resolve()
        .parents[4]
        / "assets"
        / "aws-icons"
    )

    ALIASES = {
        "s3": "simple-storage-service",
        "alb": "elastic-load-balancing",
        "elb": "elastic-load-balancing",
        "dynamodb": "dynamodb",
        "subnet": "public-subnet", # Subnets usually separate into public/private
        "securitygroup": "firewall", # Generic firewall for SG
        "vpc": "virtual-private-cloud",
        "iam": "identity-and-access-management",
        "kms": "key-management-service",
        "cloudwatch": "cloudwatch",
        "cloudtrail": "cloudtrail",
        "guardduty": "guardduty",
        "sns": "simple-notification-service",
        "ebs": "elastic-block-store",
        "efs": "elastic-file-system",
        "ecs": "elastic-container-service",
        "eks": "elastic-kubernetes-service"
    }

    _index = {}
    _is_initialized = False
    FALLBACK_ICON = None

    @classmethod
    def _normalize_name(cls, filename: str) -> str:
        """
        Removes Arch_, Res_, Amazon-, AWS-, _48, etc. from filenames to create a stable key.
        """
        name = re.sub(r"^(Arch_|Res_|Category_)", "", filename, flags=re.IGNORECASE)
        name = re.sub(r"^(Amazon-|AWS-)", "", name, flags=re.IGNORECASE)
        name = re.sub(r"_[0-9]+\.svg$", "", name, flags=re.IGNORECASE)
        name = re.sub(r"\.svg$", "", name, flags=re.IGNORECASE)
        return name.lower()

    @classmethod
    def _initialize(cls):
        if cls._is_initialized:
            return

        if not cls.BASE_DIR.exists():
            logger.warning(f"AWS icon directory not found: {cls.BASE_DIR}")
            cls._is_initialized = True
            return

        for path in cls.BASE_DIR.rglob("*.svg"):
            norm = cls._normalize_name(path.name)
            
            # Prefer architecture over resource if both exist, prefer 48px if multiple exist
            if norm not in cls._index:
                cls._index[norm] = str(path)
            else:
                existing = cls._index[norm]
                # If we haven't locked in a 48px Arch_ icon, see if this is better
                if "Arch_" in path.name and "_48" in path.name:
                    cls._index[norm] = str(path)
                elif "Arch_" in path.name and "Res_" in existing:
                    cls._index[norm] = str(path)

        # Ensure we have a default fallback
        fallback_keys = ["cloud", "aws-cloud", "general"]
        cls.FALLBACK_ICON = None
        for k in fallback_keys:
            if k in cls._index:
                cls.FALLBACK_ICON = cls._index[k]
                break

        cls._is_initialized = True

    @classmethod
    @lru_cache(maxsize=256)
    def get_icon_path(cls, resource_type: str):
        """
        Returns the absolute icon path.

        Returns generic cloud fallback if not found.
        """
        cls._initialize()

        if not resource_type:
            return cls.FALLBACK_ICON

        norm_type = resource_type.strip().lower()
        
        # Check alias map
        if norm_type in cls.ALIASES:
            norm_type = cls.ALIASES[norm_type]

        if norm_type in cls._index:
            return cls._index[norm_type]

        # Generic fallback
        logger.debug(f"Using fallback icon for unknown resource: {resource_type}")
        return cls.FALLBACK_ICON

    @classmethod
    def icon_exists(cls, resource_type: str) -> bool:
        """
        Returns True if an exact icon exists (ignoring fallback).
        """
        cls._initialize()
        if not resource_type:
            return False
        norm = resource_type.strip().lower()
        if norm in cls.ALIASES:
            norm = cls.ALIASES[norm]
        return norm in cls._index

    @classmethod
    def supported_icons(cls):
        """
        Returns every supported AWS resource alias.
        """
        cls._initialize()
        return sorted(list(cls._index.keys()) + list(cls.ALIASES.keys()))
