from fastapi import APIRouter
from app.services.topology_service import TopologyService

router = APIRouter(prefix="/api/topology", tags=["Topology"])

topology_service = TopologyService()


@router.get("/graph")
async def get_graph():
    return topology_service.get_graph()


@router.get("/nodes")
async def get_nodes():
    return topology_service.get_nodes()


@router.get("/edges")
async def get_edges():
    return topology_service.get_edges()


@router.get("/resource/{resource_id}")
async def get_resource(resource_id: str):
    return topology_service.get_resource(resource_id)


@router.get("/blast-radius/{resource_id}")
async def blast_radius(resource_id: str):
    return topology_service.blast_radius(resource_id)
