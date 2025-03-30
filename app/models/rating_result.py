from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, JSON, Float
from app.models.base import Base

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
    report_path: Optional[str] = None
    scores: Optional[str] = None
    knowledge_base_score: Optional[float] = None
    model_type: Optional[str] = None


class RatingResultRead(RatingResultCreate):
    id: Optional[int] = None
    status: str = 'requested'
    report_path: Optional[str] = None
    scores: Optional[str] = None
    knowledge_base_score: Optional[float] = None
    model_type: Optional[str] = None

    class Config:
        orm_mode = True 