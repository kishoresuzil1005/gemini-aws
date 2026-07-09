from fastapi import APIRouter

from app.services.diagram.relationship_analyzer import (
    RelationshipAnalyzer
)

router = APIRouter(

    prefix="/api/v1/architecture/diagrams",

    tags=["Architecture Diagram"]

)

service = RelationshipAnalyzer()


@router.get("/relationships")

def relationships():

    return service.analyze()
