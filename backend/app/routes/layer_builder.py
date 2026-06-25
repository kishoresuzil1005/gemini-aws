from fastapi import APIRouter

from app.services.diagram.layer_builder import LayerBuilder

router = APIRouter(

    prefix="/api/diagram",

    tags=["Diagram"]

)

builder = LayerBuilder()


@router.get("/layers")
def layers():

    return builder.build()
