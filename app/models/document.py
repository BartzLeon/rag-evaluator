from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.models.base import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    status = Column(String, nullable=False, default="requested")
    saved_to_chroma = Column(Boolean, nullable=False, default=False)
    embedding_model = Column(String, nullable=False, default="openai/text-embedding-3-large")


class DocumentCreate(BaseModel):
    name: str
    created_at: Optional[str] = None
    status: Optional[str] = None
    saved_to_chroma: bool = False
    embedding_model: str = "openai/text-embedding-3-large"


class DocumentRead(BaseModel):
    id: int
    name: str
    created_at: str
    status: str
    saved_to_chroma: bool
    embedding_model: str

    class Config:
        orm_mode = True 