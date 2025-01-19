from typing import List
from pydantic import BaseModel, Field

class CreateTestsetDTO(BaseModel):
    name: str = Field(..., description="Name of the document")
    document: int = Field(..., description="Document ID")
    model_type: str = Field(..., description="Model type eg. gpt3.5-turbo")