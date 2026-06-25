from fastapi import APIRouter

from app.services.diagram.architecture_model_builder import ArchitectureModelBuilder

router = APIRouter(

    prefix="/api/diagram",

    tags=["Diagram"]

)

builder = ArchitectureModelBuilder()


@router.get("/layers")
def layers():

    return builder.build()
