from typing import Callable, Any
from fastapi import Request, Response, HTTPException

class APIGateway:
    """
    Central API Gateway to handle rate limiting, tenant injection, and auth validation.
    """
    def __init__(self, jwt_manager):
        self.jwt_manager = jwt_manager

    async def middleware(self, request: Request, call_next: Callable) -> Response:
        # Extract token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            raise HTTPException(status_code=401, detail="Unauthorized")
            
        claims = self.jwt_manager.verify_token(token)
        if not claims:
            raise HTTPException(status_code=401, detail="Invalid token")
            
        # Inject tenant ID into request context
        request.state.tenant_id = claims.get("tenant_id")
        request.state.user_id = claims.get("sub")
        
        # Proceed with request
        response = await call_next(request)
        return response
