from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Text, JSON, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)


class RatingResult(Base):
    __tablename__ = "rating_results"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, nullable=True)
    report_path = Column(String, nullable=True)
    scores = Column(JSON, nullable=True)
    knowledge_base_score = Column(Float, nullable=True)
    model_type = Column(String, nullable=True)


class RatingResultCreate(BaseModel):
    status: str = 'created'
    report_path: str = None
    scores: str = None
    knowledge_base_score: float = None
    model_type: str = None

class RatingResultRead(RatingResultCreate):
    id: int = None
    status: str = 'created'
    report_path: str = None
    scores: str = None
    knowledge_base_score: float = None
    model_type: str = None

    class Config:
        orm_mode = True