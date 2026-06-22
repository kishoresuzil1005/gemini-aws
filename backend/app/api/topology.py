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


@router.get("/debug")
async def debug_graph():
    graph = topology_service._get_graph()
    return {
        "success": True,
        "node_count": len(graph.get("nodes", [])),
        "edge_count": len(graph.get("edges", [])),
        "sample_nodes": graph.get("nodes", [])[:5],
        "sample_edges": graph.get("edges", [])[:5]
    }


@router.post("/refresh")
async def refresh_topology():
    topology_service._graph_cache = None
    graph = topology_service._get_graph()
    return {
        "success": True,
        "nodes": len(graph["nodes"]),
        "edges": len(graph["edges"])
    }

