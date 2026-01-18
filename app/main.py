from app.core.config import settings
from app.core.middleware import TenantMiddleware
from app.api.v1.endpoints import documents

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="High-performance document search API with multi-tenancy support.",
    version="0.1.0"
)

app.add_middleware(TenantMiddleware)

app.include_router(documents.router, prefix=f"{settings.API_V1_STR}/documents", tags=["documents"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "services": {"database": "unknown", "search": "unknown"}}

@app.get("/")
async def root():
    return {"message": "Distributed Document Search Service is running"}
