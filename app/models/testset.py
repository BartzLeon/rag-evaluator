from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime
from app.models.base import Base

class Testset(Base):
    __tablename__ = "testsets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    status = Column(String, nullable=False, default="requested")
    model_type = Column(String, nullable=False)
    embedding_model = Column(String, nullable=False, default="openai/text-embedding-3-large")
    document = Column(Integer, nullable=False)
    num_questions = Column(Integer, nullable=False, default=60)
    agent_description = Column(String, nullable=False, default="A chatbot answering questions about the Machine Learning School Website")


class TestsetCreate(BaseModel):
    name: str
    created_at: Optional[str] = None
    status: Optional[str] = None
    model_type: Optional[str] = None
    embedding_model: Optional[str] = ""
    document: Optional[int] = None
    num_questions: int = 60
    agent_description: str = "A chatbot answering questions about the Machine Learning School Website"


class TestsetRead(BaseModel):
    id: int
    name: str
    created_at: str
    status: str
    model_type: str
    document: int
    num_questions: int
    agent_description: str
    embedding_model: str
    
    class Config:
        orm_mode = True 