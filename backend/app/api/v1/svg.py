from fastapi import APIRouter
from fastapi.responses import Response

from app.services.diagram.svg_renderer import SVGRenderer

router = APIRouter(

    prefix="/api/v1/architecture/diagrams",

    tags=["Architecture Diagram"]

)

renderer = SVGRenderer()


@router.get("/svg")
def svg():

    return Response(

        content=renderer.render(),

        media_type="image/svg+xml"

    )
