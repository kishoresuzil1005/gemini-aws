from fastapi import APIRouter

from app.services.diagram.graph_parser import GraphParser

router = APIRouter(
    prefix="/api/v1/architecture/diagrams",
    tags=["Diagram"]
)

parser = GraphParser()


@router.get("/graph")
def graph():

    return parser.parse()
