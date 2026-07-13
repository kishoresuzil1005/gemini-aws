from dataclasses import dataclass


@dataclass(frozen=True)
class CanvasTheme:
    background: str = "#F8FAFC"
    border: str = "#CBD5E1"


@dataclass(frozen=True)
class AccountTheme:
    fill: str = "#FFFFFF"
    border: str = "#607D8B"
    title_color: str = "#263238"


@dataclass(frozen=True)
class VPCTheme:
    fill: str = "#E8F1FE"
    border: str = "#90A4AE"
    title_color: str = "#263238"


@dataclass(frozen=True)
class AvailabilityZoneTheme:
    fill: str = "#F5F8FC"
    border: str = "#CFD8DC"
    title_color: str = "#37474F"


@dataclass(frozen=True)
class SubnetTheme:
    public_fill: str = "#E3F2FD"
    private_fill: str = "#ECEFF1"
    border: str = "#B0BEC5"


@dataclass(frozen=True)
class NodeTheme:
    fill: str = "#FFFFFF"
    border: str = "#607D8B"
    radius: int = 10
    shadow: str = "#D0D7DE"


@dataclass(frozen=True)
class EdgeTheme:
    color: str = "#607D8B"
    width: int = 2
    arrow_color: str = "#607D8B"


@dataclass(frozen=True)
class TextTheme:
    primary: str = "#263238"
    secondary: str = "#607D8B"
    font_family: str = "Arial"

    account_size: int = 24
    vpc_size: int = 18
    az_size: int = 15
    node_size: int = 13
    metadata_size: int = 10


class ThemeManager:
    """
    Enterprise diagram theme.

    All renderers should use this class instead of
    hardcoding colors, fonts or border styles.
    """

    def __init__(self):

        self.canvas = CanvasTheme()

        self.account = AccountTheme()

        self.vpc = VPCTheme()

        self.az = AvailabilityZoneTheme()

        self.subnet = SubnetTheme()

        self.node = NodeTheme()

        self.edge = EdgeTheme()

        self.text = TextTheme(