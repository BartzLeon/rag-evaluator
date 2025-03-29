from langchain_core.embeddings import Embeddings
from app.embeddings.langchain.creator.ollama_creator import OllamaEmbeddingsCreator
from app.embeddings.langchain.creator.openai_creator import OpenAIEmbeddingsCreator
from ..base_factory import BaseEmbeddingsFactory

class LangChainEmbeddingsFactory(BaseEmbeddingsFactory):
    def __init__(self):
        super().__init__()
        self._creators = {
            "nomic-embed-text:latest": OllamaEmbeddingsCreator,
            "text-embedding-3-large": OpenAIEmbeddingsCreator,
        }

    def get_embeddings(self, embedding_type: str, **kwargs) -> Embeddings:
        return super().get_embeddings(embedding_type, **kwargs) 