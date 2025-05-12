from langchain_ollama import OllamaEmbeddings
from app.embeddings.langchain.creator.base import LangchainEmbeddingsCreator

class OllamaEmbeddingsCreator(LangchainEmbeddingsCreator):
    def __init__(self, model: str = "nomic-embed-text:latest", base_url: str = "http://host.docker.internal:11434"):
        # Strip ollama/ prefix if it exists
        if model.startswith("ollama/"):
            model = model[7:]  # Remove "ollama/" prefix
        self.model = model
        self.base_url = base_url

    def create_embeddings(self) -> OllamaEmbeddings:
        return OllamaEmbeddings(
            model=self.model,
            base_url=self.base_url
        )