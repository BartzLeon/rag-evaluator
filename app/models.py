import time
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Text, JSON, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)


class RatingResult(Base):
    __tablename__ = "rating_results"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, nullable=True, default="requested")
    report_path = Column(String, nullable=True)
    scores = Column(JSON, nullable=True)
    knowledge_base_score = Column(Float, nullable=True)
    model_type = Column(String, nullable=True)


class RatingResultCreate(BaseModel):
    status: str = 'requested'
    report_path: str = None
    scores: str = None
    knowledge_base_score: float = None
    model_type: str = None

class RatingResultRead(RatingResultCreate):
    id: int = None
    status: str = 'requested'
    report_path: str = None
    scores: str = None
    knowledge_base_score: float = None
    model_type: str = None

    class Config:
        orm_mode = True


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    status = Column(String, nullable=False, default="requested")
    saved_to_chroma = Column(Boolean, nullable=False, default=False)


class DocumentCreate(BaseModel):
    name: str
    created_at: str = None
    status: str = None
    saved_to_chroma: bool = False

class DocumentRead(DocumentCreate):
    id: int
    name: str
    created_at: str
    status: str
    saved_to_chroma: bool

    class Config:
        orm_mode = True

class Testset(Base):
    __tablename__ = "testsets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    status = Column(String, nullable=False, default="requested")
    model_type = Column(String, nullable=False)
    document = Column(Integer, nullable=False)
    num_questions = Column(Integer, nullable=False, default=60)
    agent_description = Column(String, nullable=False, default="A chatbot answering questions about the Machine Learning School Website")

class TestsetCreate(BaseModel):
    name: str
    created_at: str = None
    status: str = None
    model_type: str = None
    document: int = None
    num_questions: int = 60
    agent_description: str = "A chatbot answering questions about the Machine Learning School Website"

class TestsetRead(TestsetCreate):
    id: int
    name: str
    created_at: str
    status: str
    model_type: str
    document: int
    num_questions: int
    agent_description: str

    class Config:
        orm_mode = True