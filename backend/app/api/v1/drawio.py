from fastapi import APIRouter
from fastapi.responses import Response

from app.services.diagram.drawio_generator import DrawIOGenerator

router = APIRouter(

    prefix="/api/v1/architecture/diagrams",

    tags=["Architecture Diagram"]

)

generator = DrawIOGenerator()


@router.get("/drawio")

def drawio():

    xml = generator.generate()

    return Response(

        content=xml,

        media_type="application/xml",

        headers={

            "Content-Disposition":

            "attachment; filename=architecture.drawio"

        }

    )
