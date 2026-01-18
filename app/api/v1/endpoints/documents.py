from fastapi import APIRouter, Depends, Request, HTTPException
from typing import List
from app.models.document import DocumentCreate, DocumentResponse
from app.services.document_service import document_service

router = APIRouter()

@router.post("/", response_model=DocumentResponse)
async def create_document(request: Request, doc: DocumentCreate):
    tenant_id = request.state.tenant_id
    return await document_service.create_document(tenant_id, doc)

@router.get("/search", response_model=List[DocumentResponse])
async def search_documents(request: Request, q: str):
    tenant_id = request.state.tenant_id
    return await document_service.search_documents(tenant_id, q)

@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(request: Request, doc_id: str):
    tenant_id = request.state.tenant_id
    doc = await document_service.get_document(tenant_id, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.delete("/{doc_id}")
async def delete_document(request: Request, doc_id: str):
    tenant_id = request.state.tenant_id
    deleted = await document_service.delete_document(tenant_id, doc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "success", "id": doc_id}
