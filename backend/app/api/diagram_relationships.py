from fastapi import APIRouter

from app.services.diagram.graph_parser import GraphParser
from app.services.diagram.relationship_builder import RelationshipBuilder

router = APIRouter(
    prefix="/api/diagram",
    tags=["Diagram"]
)


@router.get("/relationships")
def relationships():

    graph = GraphParser().parse()

    return RelationshipBuilder().build(graph)
