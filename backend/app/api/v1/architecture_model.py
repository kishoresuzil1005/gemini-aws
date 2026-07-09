from fastapi import APIRouter

from app.services.diagram.architecture_model_builder import (
    ArchitectureModelBuilder
)

router = APIRouter(

    prefix="/api/v1/architecture/diagrams",

    tags=["Architecture Diagram"]

)

builder = ArchitectureModelBuilder()


@router.get("/architecture-model")

def architecture_model():

    return builder.build()
