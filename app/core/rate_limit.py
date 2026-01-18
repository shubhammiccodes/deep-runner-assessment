from app.core.db import db
from fastapi import HTTPException

async def check_rate_limit(tenant_id: str, limit: int = 60, window: int = 60):
    """
    Simple Token Bucket / Window rate limiter using Redis.
    Limit: requests per window (seconds)
    """
    if not db.redis_client:
        return # Skip if redis not ready
        
    key = f"ratelimit:{tenant_id}"
    
    # Increment counter
    current = await db.redis_client.incr(key)
    
    # Set expiry on first request
    if current == 1:
        await db.redis_client.expire(key, window)
        
    if current > limit:
        raise HTTPException(
            status_code=429, 
            detail="Rate limit exceeded. Please try again later."
        )
