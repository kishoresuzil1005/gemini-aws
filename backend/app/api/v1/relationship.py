from fastapi import APIRouter

from app.services.diagram.relationship_analyzer import (
    RelationshipAnalyzer
)

router = APIRouter(

    prefix="/api/diagram",

    tags=["Architecture Diagram"]

)

service = RelationshipAnalyzer()


@router.get("/relationships")

def relationships():

    return service.analyze()
