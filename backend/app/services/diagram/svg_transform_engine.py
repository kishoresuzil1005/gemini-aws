import re


class SVGTransformEngine:
    """
    Transforms sanitized SVG fragments into positioned SVG groups.

    Responsibilities
    ----------------
    - Position icon
    - Scale icon
    - Preserve aspect ratio
    """

    DEFAULT_SIZE = 48

    VIEWBOX_PATTERN = re.compile(
        r'viewBox="([\d\.\-\s]+)"',
        re.IGNORECASE
    )

    @classmethod
    def transform(
        cls,
        svg_fragment: str,
        x: float,
        y: float,
        size: int = DEFAULT_SIZE
    ) -> str:
        """
        Returns a transformed SVG group.

        Parameters
        ----------
        svg_fragment : Sanitized SVG fragment
        x            : Target X coordinate
        y            : Target Y coordinate
        size         : Desired icon size

        Returns
        -------
        SVG <g> element
        """

        if not svg_fragment:
            return ""

        scale = 1.0

        match = cls.VIEWBOX_PATTERN.search(svg_fragment)

        if match:

            try:

                values = list(
                    map(float, match.group(1).split())
                )

                if len(values) == 4:

                    width = values[2]
                    height = values[3]

                    longest = max(width, height)

                    if longest > 0:
                        scale = size / longest

            except Exception:
                scale = 1.0

        return f"""
<g transform="translate({x},{y}) scale({scale})">
{svg_fragment}
</g>
"""
