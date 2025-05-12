from typing import List, Optional
from pydantic import BaseModel, Field
from app.dto.source_dto import SourceDTO

class CreateDocumentsDTO(BaseModel):
    name: str = Field(..., description="Name of the document")
    urls: Optional[List[str]] = Field(None, description="List of URLs to process")
    embedding_model: str = Field("openai/text-embedding-3-large", description="Embedding model to use for document vectorization")
    file_ids: Optional[List[int]] = None

    def get_sources(self) -> List[SourceDTO]:
        sources = []
        if self.urls:
            sources.extend([SourceDTO.create_url_source(url) for url in self.urls])
        return sources