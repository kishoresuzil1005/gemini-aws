from fastapi import APIRouter

from app.services.diagram.vpc_az_builder import VPCAZBuilder

router = APIRouter(

    prefix="/api/diagram",

    tags=["Architecture Diagram"]

)

builder = VPCAZBuilder()


@router.get("/vpc-layout")

def vpc_layout():

    return builder.build()
