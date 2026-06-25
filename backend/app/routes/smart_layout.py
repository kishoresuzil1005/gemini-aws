from fastapi import APIRouter

from app.services.diagram.smart_layout_engine import (
    SmartLayoutEngine
)

router = APIRouter(

    prefix="/api/diagram",

    tags=["Architecture Diagram"]

)

engine = SmartLayoutEngine()


@router.get("/smart-layout")

def smart_layout():

    return engine.build()
