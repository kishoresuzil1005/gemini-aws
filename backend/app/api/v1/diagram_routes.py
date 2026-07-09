from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Dict, Any, Optional

from app.services.diagram.svg_renderer import SVGRenderer
from app.services.diagram.drawio_generator import DrawIOGenerator

router = APIRouter(prefix="/api/ai/architecture", tags=["AI Architecture Diagram"])

class DiagramRequest(BaseModel):
    provider: str = "aws"
    format: str = "svg"
    diagram_type: Optional[str] = "infrastructure"

@router.post("/diagram")
async def generate_diagram(request: DiagramRequest):
    try:
        format_type = request.format.lower()
        
        if format_type == "svg":
            svg = SVGRenderer().render()
            return Response(
                content=svg,
                media_type="image/svg+xml"
            )
        elif format_type == "drawio":
            xml = DrawIOGenerator().generate()
            return Response(
                content=xml,
                media_type="application/xml",
                headers={
                    "Content-Disposition": "attachment; filename=architecture.drawio"
                }
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported format. Use 'svg' or 'drawio'.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
