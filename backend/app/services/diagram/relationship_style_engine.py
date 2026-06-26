from dataclasses import dataclass


@dataclass(frozen=True)
class RelationshipStyle:

    stroke: str

    width: float

    dasharray: str | None

    arrow: str

    opacity: float

    label_color: str


class RelationshipStyleEngine:
    """
    Central styling engine for all diagram relationships.
    """

    DEFAULT = RelationshipStyle(
        stroke="#607D8B",
        width=2.0,
        dasharray=None,
        arrow="arrow",
        opacity=1.0,
        label_color="#546E7A"
    )

    ATTACHED_TO = RelationshipStyle(
        stroke="#455A64",
        width=2.5,
        dasharray=None,
        arrow="arrow",
        opacity=1.0,
        label_color="#455A64"
    )

    CONNECTS_TO = RelationshipStyle(
        stroke="#1E88E5",
        width=2.5,
        dasharray=None,
        arrow="arrow",
        opacity=1.0,
        label_color="#1565C0"
    )

    RUNS_IN = RelationshipStyle(
        stroke="#43A047",
        width=2.0,
        dasharray="6 3",
        arrow="arrow",
        opacity=1.0,
        label_color="#2E7D32"
    )

    MEMBER_OF = RelationshipStyle(
        stroke="#8E24AA",
        width=2.0,
        dasharray="4 4",
        arrow="arrow",
        opacity=1.0,
        label_color="#6A1B9A"
    )

    DEPENDS_ON = RelationshipStyle(
        stroke="#EF6C00",
        width=2.5,
        dasharray="10 4",
        arrow="arrow",
        opacity=1.0,
        label_color="#E65100"
    )

    @classmethod
    def get_style(cls, relationship: str):

        if not relationship:
            return cls.DEFAULT

        relationship = relationship.upper()

        mapping = {
            "ATTACHED_TO": cls.ATTACHED_TO,
            "CONNECTS_TO": cls.CONNECTS_TO,
            "RUNS_IN": cls.RUNS_IN,
            "MEMBER_OF": cls.MEMBER_OF,
            "DEPENDS_ON": cls.DEPENDS_ON,
        }

        return mapping.get(
            relationship,
            cls.DEFAULT
        )
