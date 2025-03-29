from abc import ABC, abstractmethod
from langchain_core.embeddings import Embeddings

class LangchainEmbeddingsCreator(ABC):
    @abstractmethod
    def create_embeddings(self) -> Embeddings:
        """Create and return a configured Giskard Embeddings instance."""
        pass 