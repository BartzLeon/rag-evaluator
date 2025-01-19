from pydantic import BaseModel

class SourceDTO(BaseModel):
    name: str
    type: str
    url: str