from fastapi import APIRouter, Depends, Request, HTTPException
from typing import List
from app.models.document import DocumentCreate, DocumentResponse, DocumentUpdate, DocumentInDB
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=DocumentResponse)
async def create_document(request: Request, doc: DocumentCreate):
    tenant_id = request.state.tenant_id
    # TODO: Connect to MongoDB/Elasticsearch
    return DocumentInDB(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        created_at=datetime.utcnow(),
        **doc.model_dump()
    )

@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(request: Request, doc_id: str):
    tenant_id = request.state.tenant_id
    # TODO: Fetch from Storage
    return DocumentInDB(
        id=doc_id,
        tenant_id=tenant_id,
        title="Mock Document",
        content="This is a mock content for reading.",
        created_at=datetime.utcnow()
    )

@router.delete("/{doc_id}")
async def delete_document(request: Request, doc_id: str):
    tenant_id = request.state.tenant_id
    # TODO: Delete from Storage
    return {"status": "success", "id": doc_id}

@router.get("/search", response_model=List[DocumentResponse])
async def search_documents(request: Request, q: str):
    tenant_id = request.state.tenant_id
    # TODO: Search in Elasticsearch
    return []
