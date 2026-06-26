from dataclasses import dataclass


@dataclass(frozen=True)
class FontStyle:

    family: str

    size: int

    weight: str

    color: str


class TypographyEngine:
    """
    Central typography configuration for the SVG renderer.
    """

    ACCOUNT = FontStyle(
        family="Arial",
        size=24,
        weight="bold",
        color="#263238"
    )

    VPC = FontStyle(
        family="Arial",
        size=18,
        weight="bold",
        color="#263238"
    )

    AZ = FontStyle(
        family="Arial",
        size=15,
        weight="bold",
        color="#37474F"
    )

    NODE = FontStyle(
        family="Arial",
        size=13,
        weight="bold",
        color="#263238"
    )

    METADATA = FontStyle(
        family="Arial",
        size=10,
        weight="normal",
        color="#607D8B"
    )

    LEGEND = FontStyle(
        family="Arial",
        size=11,
        weight="normal",
        color="#455A64"
    )

    FOOTER = FontStyle(
        family="Arial",
        size=9,
        weight="normal",
        color="#78909C"
    )

    @staticmethod
    def truncate(text: str, limit: int = 28):

        if not text:
            return ""

        if len(text) <= limit:
            return text

        return text[:limit - 3] + "..."

    @staticmethod
    def wrap(text: str, limit: int = 22):

        if not text:
            return []

        words = text.split()

        lines = []

        current = ""

        for word in words:

            if len(current + " " + word) <= limit:

                current = (current + " " + word).strip()

            else:

                lines.append(current)

                current = word

        if current:

            lines.append(current)

        return lines
