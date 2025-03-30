from langchain_core.embeddings import Embeddings
from app.embeddings.langchain.creator.ollama_creator import OllamaEmbeddingsCreator
from app.embeddings.langchain.creator.openai_creator import OpenAIEmbeddingsCreator

class LangChainEmbeddingsFactory():
    _creators = {
        "ollama/nomic-embed-text:latest": OllamaEmbeddingsCreator,
        "openai/text-embedding-3-large": OpenAIEmbeddingsCreator,
    }

    def get_embeddings(self, embedding_type: str, **kwargs) -> Embeddings:
        creator_class = self._creators.get(embedding_type.lower())
        if not creator_class:
            raise ValueError(f"Unsupported embedding type: {embedding_type}")
        creator = creator_class(**kwargs)
        return creator.create_embeddings()

    @classmethod
    def set_global_embedding_model(cls, model_type: str, **kwargs):
        pass

    @classmethod
    def reset_global_embedding_model(cls):
        pass