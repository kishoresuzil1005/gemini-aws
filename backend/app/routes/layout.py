from fastapi import APIRouter

from app.services.diagram.layout_engine import LayoutEngine

router = APIRouter(

    prefix="/api/diagram",

    tags=["Architecture Diagram"]

)

engine = LayoutEngine()


@router.get("/layout")
def layout():

    return engine.build()
