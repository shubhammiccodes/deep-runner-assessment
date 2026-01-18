from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class DocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    
class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class DocumentInDB(DocumentBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Project Proposal",
                "content": "This is the content of the document...",
                "tenant_id": "tenant-1",
                "created_at": "2024-01-18T12:00:00Z"
            }
        }

class DocumentResponse(DocumentInDB):
    pass
