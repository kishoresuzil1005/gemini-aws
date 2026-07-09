from fastapi import APIRouter

from app.services.diagram.aws_icon_mapper import AWSIconMapper

router = APIRouter(

    prefix="/api/v1/architecture/diagrams",

    tags=["Architecture Diagram"]

)

mapper = AWSIconMapper()


@router.get("/icons")
def icons():

    return mapper.build()
