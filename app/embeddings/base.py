from abc import ABC, abstractmethod

from langchain_core.embeddings import Embeddings


class EmbeddingsCreator(ABC):

    @abstractmethod
    def create_embeddings(self) -> Embeddings:
        """Create and return a configured Embeddings instance."""
        pass