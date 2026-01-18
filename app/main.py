from fastapi import FastAPI

app = FastAPI(
    title="Distributed Document Search Service",
    description="High-performance document search API with multi-tenancy support.",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"message": "Distributed Document Search Service is running"}
