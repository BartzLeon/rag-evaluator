from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, JSON, Float, ForeignKey, DateTime
from app.models.base import Base
from datetime import datetime

class RatingResult(Base):
    __tablename__ = "rating_results"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, nullable=True, default="requested")
    report_path = Column(String, nullable=True)
    scores = Column(JSON, nullable=True)
    knowledge_base_score = Column(Float, nullable=True)
    llm_to_be_evaluated_type = Column(String, nullable=True)
    judge_llm_type = Column(String, nullable=True)
    testset_id = Column(Integer, ForeignKey("testsets.id"), nullable=True)
    start_eval = Column(DateTime, nullable=True)
    end_eval = Column(DateTime, nullable=True)
    time_eval = Column(Float, nullable=True)  # Duration in seconds


class RatingResultCreate(BaseModel):
    status: str = 'requested'
    report_path: Optional[str] = None
    scores: Optional[str] = None
    knowledge_base_score: Optional[float] = None
    llm_to_be_evaluated_type: Optional[str] = None
    judge_llm_type: Optional[str] = None
    testset_id: Optional[int] = None
    start_eval: Optional[datetime] = None
    end_eval: Optional[datetime] = None
    time_eval: Optional[float] = None


class RatingResultRead(RatingResultCreate):
    id: Optional[int] = None
    status: str = 'requested'
    report_path: Optional[str] = None
    scores: Optional[str] = None
    knowledge_base_score: Optional[float] = None
    llm_to_be_evaluated_type: Optional[str] = None
    judge_llm_type: Optional[str] = None
    testset_id: Optional[int] = None
    start_eval: Optional[datetime] = None
    end_eval: Optional[datetime] = None
    time_eval: Optional[float] = None

    class Config:
        orm_mode = True 