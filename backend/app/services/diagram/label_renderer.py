from app.services.diagram.typography_engine import TypographyEngine
from app.services.diagram.label_engine import LabelEngine
from app.services.diagram.label_layout import LabelLayout
from app.services.diagram.label_collision_detector import LabelCollisionDetector
from app.services.diagram.tooltip_renderer import TooltipRenderer


class LabelRenderer:

    def __init__(self):

        self.detector = LabelCollisionDetector()

    def render(self, svg, nodes):

        for node in nodes:

            layout = LabelLayout.compute(node)

            title = LabelEngine.title(node)

            meta = LabelEngine.metadata(node)

            TooltipRenderer.render(
                svg,
                LabelEngine.tooltip(node)
            )

            title_style = TypographyEngine.NODE

            if self.detector.allow(
                layout["title_x"] - 60,
                layout["title_y"] - 12,
                120,
                16
            ):

                svg.append(f"""
<text
x="{layout['title_x']}"
y="{layout['title_y']}"
text-anchor="middle"
font-family="{title_style.family}"
font-size="{title_style.size}"
font-weight="{title_style.weight}"
fill="{title_style.color}">
{title}
</text>
""")

            meta_style = TypographyEngine.METADATA

            if self.detector.allow(
                layout["meta_x"] - 60,
                layout["meta_y"] - 10,
                120,
                14
            ):

                svg.append(f"""
<text
x="{layout['meta_x']}"
y="{layout['meta_y']}"
text-anchor="middle"
font-family="{meta_style.family}"
font-size="{meta_style.size}"
fill="{meta_style.color}">
{meta}
</text>
"""