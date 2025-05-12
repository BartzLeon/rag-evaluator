from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class FileCreateDTO(BaseModel):
    filename: str
    file_path: str

class FileReadDTO(BaseModel):
    id: int
    filename: str
    file_path: str
    created_at: datetime
    document_id: Optional[int] = None

    class Config:
        from_attributes = True 