from fastapi import APIRouter

from app.services.diagram.resource_aggregator import ResourceAggregator

router = APIRouter(
    prefix="/api/diagram",
    tags=["Architecture Diagram"]
)

aggregator = ResourceAggregator()


@router.get("/aggregate")
def aggregate():

    return aggregator.build()
