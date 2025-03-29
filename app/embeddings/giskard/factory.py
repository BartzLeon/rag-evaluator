from giskard.llm.embeddings import BaseEmbedding
from ..base_factory import BaseEmbeddingsFactory
from .creator import GiskardOllamaEmbeddingsCreator

class GiskardEmbeddingsFactory(BaseEmbeddingsFactory):
    def __init__(self):
        super().__init__()
        self._creators = {
            "ollama/nomic-embed-text:latest": GiskardOllamaEmbeddingsCreator,
        }

    def get_embeddings(self, model: str, **kwargs) -> BaseEmbedding:
        return super().get_embeddings(model, **kwargs) 