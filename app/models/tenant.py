from pydantic import BaseModel

class TenantConfig(BaseModel):
    tenant_id: str
    rate_limit: int = 100 # Requests per minute
