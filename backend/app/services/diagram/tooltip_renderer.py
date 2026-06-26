class TooltipRenderer:

    @staticmethod
    def render(svg, text):

        svg.append(f"""
<title>
{text}
</title>
""")
