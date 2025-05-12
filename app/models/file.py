from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.association import file_document

class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    
    # Many-to-many relationship with documents
    documents = relationship("Document", secondary=file_document, back_populates="files")

    class Config:
        from_attributes = True