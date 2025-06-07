from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.dto.file_dto import FileReadDTO
from app.models.association import file_document

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    embedding_model = Column(String, nullable=False)
    status = Column(String, nullable=False, default="Processing")
    saved_to_chroma = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    repos = Column(JSON, nullable=True, default=list)  # Changed to nullable=False
    
    # Many-to-many relationship with files
    files = relationship("UploadedFile", secondary=file_document, back_populates="documents")

    def to_read_model(self) -> 'DocumentRead':
        """Convert to DocumentRead model with proper defaults"""
        return DocumentRead(
            id=getattr(self, 'id'),
            name=str(getattr(self, 'name')),
            created_at=getattr(self, 'created_at'),
            status=str(getattr(self, 'status')),
            saved_to_chroma=bool(getattr(self, 'saved_to_chroma')),
            embedding_model=str(getattr(self, 'embedding_model')),
            files=getattr(self, 'files') or [],
            urls=[],  # This will be populated from sources if needed
            repos=getattr(self, 'repos') or []
        )

    class Config:
        from_attributes = True


class DocumentCreate(BaseModel):
    name: str
    created_at: str = datetime.now().isoformat()
    status: Optional[str] = None
    saved_to_chroma: bool = False
    embedding_model: str = "openai/text-embedding-3-large"
    repos: Optional[List[str]] = []

    class Config:
        from_attributes = True


class DocumentRead(BaseModel):
    id: int
    name: str
    created_at: datetime
    status: str
    saved_to_chroma: bool
    embedding_model: str
    files: List[FileReadDTO] = []
    urls: List[str] = []
    repos: List[str] = []

    class Config:
        from_attributes = True
