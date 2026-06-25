from fastapi import APIRouter
from fastapi.responses import Response

from app.services.diagram.svg_renderer import SVGRenderer
from app.services.diagram.drawio_generator import DrawIOGenerator

router = APIRouter(
    prefix="/api/ai/architecture",
    tags=["AI Architecture"]
)


@router.post("/diagram")
async def generate_diagram(request: dict):

    fmt = request.get("format", "svg").lower()

    #
    # SVG
    #

    if fmt == "svg":

        svg = SVGRenderer().render()

        return Response(
            content=svg,
            media_type="image/svg+xml"
        )

    #
    # Draw.io
    #

    if fmt == "drawio":

        xml = DrawIOGenerator().generate()

        return Response(
            content=xml,
            media_type="application/xml"
        )

    return {
        "error": "Unsupported format"
    }
