from langchain_community.embeddings import OllamaEmbeddings

from .base import EmbeddingsCreator

class OllamaEmbeddingsCreator(EmbeddingsCreator):
    def __init__(self, model: str = "nomic-embed-text:latest", base_url: str = "http://host.docker.internal:11434"):
        self.model = model
        self.base_url = base_url

    def create_embeddings(self) -> OllamaEmbeddings:
        return OllamaEmbeddings(
            model=self.model,
            base_url=self.base_url
        )