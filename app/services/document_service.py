from app.core.db import db
from app.core.config import settings
from app.models.document import DocumentCreate, DocumentInDB
from datetime import datetime
import uuid

class DocumentService:
    def __init__(self):
        self.mongo = db.mongo_client[settings.MONGODB_DB_NAME]
        self.es = db.es_client

    async def create_document(self, tenant_id: str, doc: DocumentCreate) -> DocumentInDB:
        doc_id = str(uuid.uuid4())
        document = DocumentInDB(
            id=doc_id,
            tenant_id=tenant_id,
            created_at=datetime.utcnow(),
            **doc.model_dump()
        )
        doc_dict = document.model_dump()
        
        # 1. Store in MongoDB (Source of Truth)
        await self.mongo.documents.insert_one(doc_dict)
        
        # 2. Index in Elasticsearch (Search)
        await self.es.index(
            index="documents",
            id=doc_id,
            document={
                "title": doc.title,
                "content": doc.content,
                "tenant_id": tenant_id,
                "created_at": doc.created_at
            }
        )
        return document

    async def get_document(self, tenant_id: str, doc_id: str) -> DocumentInDB:
        doc = await self.mongo.documents.find_one({"id": doc_id, "tenant_id": tenant_id})
        if doc:
            return DocumentInDB(**doc)
        return None

    async def delete_document(self, tenant_id: str, doc_id: str) -> bool:
        result = await self.mongo.documents.delete_one({"id": doc_id, "tenant_id": tenant_id})
        if result.deleted_count > 0:
            try:
                await self.es.delete(index="documents", id=doc_id)
            except Exception:
                # Log error but don't fail if ES is out of sync
                pass
            return True
        return False

    async def search_documents(self, tenant_id: str, query: str):
        # Elasticsearch Query with Tenant Isolation
        body = {
            "query": {
                "bool": {
                    "must": [
                        {"multi_match": {"query": query, "fields": ["title", "content"]}}
                    ],
                    "filter": [
                        {"term": {"tenant_id": tenant_id}}
                    ]
                }
            }
        }
        
        response = await self.es.search(index="documents", body=body)
        hits = response['hits']['hits']
        
        results = []
        for hit in hits:
            source = hit['_source']
            results.append(DocumentInDB(
                id=hit['_id'],
                tenant_id=source['tenant_id'],
                title=source['title'],
                content=source['content'],
                created_at=source['created_at']
            ))
        return results

document_service = DocumentService()
