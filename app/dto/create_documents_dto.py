from typing import List, Optional
from pydantic import BaseModel, Field
from app.dto.source_dto import SourceDTO
import os

class CreateDocumentsDTO(BaseModel):
    name: str = Field(..., description="Name of the document")
    urls: Optional[List[str]] = Field(None, description="List of URLs to process")
    repos: Optional[List[str]] = Field(None, description="List of git repository names in data/repos folder")
    embedding_model: str = Field("openai/text-embedding-3-large", description="Embedding model to use for document vectorization")
    file_ids: Optional[List[int]] = None

    def get_sources(self) -> List[SourceDTO]:
        sources = []
        if self.urls:
            sources.extend([SourceDTO.create_url_source(url) for url in self.urls])
        
        # Add git repository sources
        if self.repos:
            for repo_name in self.repos:
                repo_path = f"app/data/repos/{repo_name}"
                # Check if the repository exists in the repos folder
                if os.path.exists(repo_path) and os.path.isdir(repo_path):
                    sources.append(SourceDTO.create_git_source(repo_path))
                else:
                    raise ValueError(f"Repository '{repo_name}' not found in data/repos folder")
        
        return sources