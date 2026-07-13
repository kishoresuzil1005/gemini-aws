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

    IN_SUBNET = RelationshipStyle(
        stroke="#42A5F5",
        width=2.0,
        dasharray="6 3",
        arrow="arrow",
        opacity=1.0,
        label_color="#1E88E5"
    )

    IN_VPC = RelationshipStyle(
        stroke="#5C6BC0",
        width=2.2,
        dasharray="8 4",
        arrow="arrow",
        opacity=1.0,
        label_color="#3949AB"
    )

    USES_ROLE = RelationshipStyle(
        stroke="#8E24AA",
        width=2.0,
        dasharray="3 3",
        arrow="arrow",
        opacity=1.0,
        label_color="#6A1B9A"
    )

    ATTACHED_VOLUME = RelationshipStyle(
        stroke="#546E7A",
        width=2.5,
        dasharray=None,
        arrow="arrow",
        opacity=1.0,
        label_color="#455A64"
    )

    @classmethod
    def get_style(cls, relationship: str):

        if not relationship:
            return cls.DEFAULT

        relationship = relationship.upper()

        mapping = {
            "ATTACHED_TO": cls.ATTACHED_TO,
            "ATTACHED_VOLUME": cls.ATTACHED_VOLUME,
            "CONNECTS_TO": cls.CONNECTS_TO,
            "RUNS_IN": cls.RUNS_IN,
            "IN_SUBNET": cls.IN_SUBNET,
            "IN_VPC": cls.IN_VPC,
            "MEMBER_OF": cls.MEMBER_OF,
            "USES_ROLE": cls.USES_ROLE,
            "DEPENDS_ON": cls.DEPENDS_ON,
        }

        return mapping.get(
            relationship,
            cls.DEFAULT
        )