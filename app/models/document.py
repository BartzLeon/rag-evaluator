from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, Boolean
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
    
    # Many-to-many relationship with files
    files = relationship("UploadedFile", secondary=file_document, back_populates="documents")

    class Config:
        from_attributes = True


class DocumentCreate(BaseModel):
    name: str
    created_at: str = datetime.now().isoformat()
    status: Optional[str] = None
    saved_to_chroma: bool = False
    embedding_model: str = "openai/text-embedding-3-large"

    class Config:
        from_attributes = True


class DocumentRead(BaseModel):
    id: int
    name: str
    created_at: datetime
    status: str
    saved_to_chroma: bool
    embedding_model: str
    files: List[FileReadDTO]
    urls: List[str] = []

    class Config:
        from_attributes = True
