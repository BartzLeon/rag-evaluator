from typing import List
from pydantic import BaseModel, Field
from app.dto.source_dto import SourceDTO

class CreateDocumentsDTO(BaseModel):
    name: str = Field(..., description="Name of the document")
    sources: List[SourceDTO] | None = None