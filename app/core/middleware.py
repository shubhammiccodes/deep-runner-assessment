from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Allow health checks without tenant ID
        if request.url.path == "/health" or request.url.path == "/":
            return await call_next(request)
            
        tenant_id = request.headers.get("X-Tenant-ID") or request.query_params.get("tenant_id")
        
        if not tenant_id:
            # For simplicity/prototype, we return 400. 
            # In a real app, strict auth logic would go here.
            # We return JSON response manually because exceptions in middleware 
            # can be tricky depending on exception handlers.
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=400, 
                content={"detail": "X-Tenant-ID header or tenant_id query param is required"}
            )
            
        # Inject tenant_id into request state for endpoints to use
        request.state.tenant_id = tenant_id
        
        response = await call_next(request)
        return response
