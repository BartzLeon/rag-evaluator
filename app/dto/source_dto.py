from typing import Literal
from pydantic import BaseModel, Field

class SourceDTO(BaseModel):
    type: Literal["url", "file", "git"] = Field(..., description="Type of the source (url, file, or git)")
    url: str | None = Field(None, description="URL of the source if type is 'url'")
    file_path: str | None = Field(None, description="Path to the file if type is 'file'")
    repo_path: str | None = Field(None, description="Path to the git repository if type is 'git'")

    @classmethod
    def create_url_source(cls, url: str) -> "SourceDTO":
        return cls(type="url", url=url, file_path=None, repo_path=None)

    @classmethod
    def create_file_source(cls, file_path: str) -> "SourceDTO":
        return cls(type="file", file_path=file_path, url=None, repo_path=None)

    @classmethod
    def create_git_source(cls, repo_path: str) -> "SourceDTO":
        return cls(type="git", repo_path=repo_path, url=None, file_path=None)