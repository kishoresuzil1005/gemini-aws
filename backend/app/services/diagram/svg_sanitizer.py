import re


class SVGSanitizer:
    """
    Cleans raw SVG files before embedding.

    Responsibilities

    - remove XML declaration
    - remove DOCTYPE
    - remove comments
    - remove outer SVG tag
    - return inner SVG markup
    """

    XML_PATTERN = re.compile(
        r"<\?xml.*?\?>",
        flags=re.DOTALL | re.IGNORECASE
    )

    DOCTYPE_PATTERN = re.compile(
        r"<!DOCTYPE.*?>",
        flags=re.DOTALL | re.IGNORECASE
    )

    COMMENT_PATTERN = re.compile(
        r"<!--.*?-->",
        flags=re.DOTALL
    )

    OPEN_SVG_PATTERN = re.compile(
        r"<svg[^>]*>",
        flags=re.IGNORECASE
    )

    CLOSE_SVG_PATTERN = re.compile(
        r"</svg>",
        flags=re.IGNORECASE
    )

    @classmethod
    def sanitize(cls, svg: str) -> str:
        """
        Return sanitized SVG fragment.

        Returns
        -------
        Inner SVG markup.
        """

        if not svg:
            return ""

        svg = cls.XML_PATTERN.sub("", svg)

        svg = cls.DOCTYPE_PATTERN.sub("", svg)

        svg = cls.COMMENT_PATTERN.sub("", svg)

        svg = cls.OPEN_SVG_PATTERN.sub("", svg)

        svg = cls.CLOSE_SVG_PATTERN.sub("", svg)

        return svg.strip()
