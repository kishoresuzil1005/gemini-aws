from fastapi import APIRouter, Query
from typing import Optional
from app.services.topology.topology_service import TopologyService

router = APIRouter(prefix="/api/v1/topology", tags=["Topology"])

topology_service = TopologyService()


@router.get("/graph")
async def get_graph(region: Optional[str] = Query(None, description="Filter graph nodes by AWS region")):
    return topology_service.get_graph(region=region)


@router.get("/nodes")
async def get_nodes(region: Optional[str] = Query(None, description="Filter nodes by AWS region")):
    return topology_service.get_nodes(region=region)


@router.get("/edges")
async def get_edges(region: Optional[str] = Query(None, description="Filter edges by AWS region")):
    return topology_service.get_edges(region=region)


@router.get("/resource/{resource_id}")
async def get_resource(resource_id: str):
    return topology_service.get_resource(resource_id)


@router.get("/blast-radius/{resource_id}")
async def blast_radius(resource_id: str):
    return topology_service.blast_radius(resource_id)


@router.get("/debug")
async def debug_graph(region: Optional[str] = Query(None)):
    graph = topology_service._get_graph(region=region)
    return {
        "success": True,
        "node_count": len(graph.get("nodes", [])),
        "edge_count": len(graph.get("edges", [])),
        "sample_nodes": graph.get("nodes", [])[:5],
        "sample_edges": graph.get("edges", [])[:5]
    }


@router.post("/refresh")
async def refresh_topology(region: Optional[str] = Query(None)):
    topology_service._graph_cache = None
    graph = topology_service._get_graph(region=region)
    return {
        "success": True,
        "nodes": len(graph["nodes"]),
        "edges": len(graph["edges"])
    }

