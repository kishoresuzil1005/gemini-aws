from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

router = APIRouter(prefix="/api/ai/architecture", tags=["AI Architecture Diagram"])

class DiagramRequest(BaseModel):
    provider: str = "aws"
    format: str = "svg"
    diagram_type: Optional[str] = "infrastructure"

@router.post("/diagram")
async def generate_diagram(request: DiagramRequest) -> Dict[str, Any]:
    try:
        from app.services.diagram.diagram_generator import DiagramGenerator
        generator = DiagramGenerator()
        
        result = generator.generate(
            provider=request.provider,
            format_type=request.format,
            diagram_type=request.diagram_type
        )
        
        # Depending on format, the response structure varies slightly according to spec
        response = {
            "format": result.get("format"),
            "file": result.get("file")
        }
        
        if result.get("format") == "svg":
            response["preview"] = result.get("preview")
            
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
