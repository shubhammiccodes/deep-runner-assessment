from app.core.db import db
from fastapi import Request, HTTPException

class RateLimiter:
    def __init__(self, limit: int = 60, window: int = 60):
        self.limit = limit
        self.window = window

    async def __call__(self, request: Request):
        if not db.redis_client:
            return # Skip if redis not ready
            
        # Get tenant_id from request state (set by TenantMiddleware)
        tenant_id = getattr(request.state, "tenant_id", None)
        
        if not tenant_id:
            # Middleware acts as gatekeeper, but if for some reason we are here without tenant_id
            return
            
        key = f"ratelimit:{tenant_id}"
        
        # Increment counter
        current = await db.redis_client.incr(key)
        
        # Set expiry on first request
        if current == 1:
            await db.redis_client.expire(key, self.window)
            
        if current > self.limit:
            raise HTTPException(
                status_code=429, 
                detail="Rate limit exceeded. Please try again later."
            )
