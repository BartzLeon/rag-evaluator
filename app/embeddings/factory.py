from langchain_core.embeddings import Embeddings
from .ollama_creator import OllamaEmbeddingsCreator
from .openai_creator import OpenAIEmbeddingsCreator

class EmbeddingsFactory:
    _creators = {
        "lite_llm/nomic-embed-text:latest": OllamaEmbeddingsCreator,
        "openai/text-embedding-3-large": OpenAIEmbeddingsCreator,
    }

    @classmethod
    def get_embeddings(cls, embedding_type: str, **kwargs) -> Embeddings:
        creator_class = cls._creators.get(embedding_type.lower())
        if not creator_class:
            raise ValueError(f"Unsupported embedding type: {embedding_type}")
        creator = creator_class(**kwargs)
        return creator.create_embeddings()

    @classmethod
    def available_embeddings(cls):
        return list(cls._creators.keys())