from abc import ABC, abstractmethod
from giskard.llm.embeddings import BaseEmbedding

class GiskardEmbeddingsCreator(ABC):
    @abstractmethod
    def create_embeddings(self) -> BaseEmbedding:
        """Create and return a configured Giskard Embeddings instance."""
        pass 