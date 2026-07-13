from pathlib import Path
import logging

logger = logging.getLogger("SVGLoader")


class SVGLoader:
    """
    Loads raw SVG files from disk.

    Responsibilities:
    - Validate file existence
    - Read SVG contents
    - Return raw SVG text

    Does NOT:
    - sanitize SVG
    - cache SVG
    - resize SVG
    """

    @staticmethod
    def load(path: str) -> str | None:
        """
        Load an SVG file.

        Returns:
            SVG string

        Returns None if loading fails.
        """

        if not path:
            return None

        try:

            file_path = Path(path)

            if not file_path.exists():
                logger.warning(f"SVG icon not found: {path}")
                return None

            if not file_path.is_file():
                logger.warning(f"Not a file: {path}")
                return None

            return file_path.read_text(
                encoding="utf-8"
            )

        except Exception as e:

            logger.exception(
                f"Unable to load SVG: {path}"
            )

            return Non