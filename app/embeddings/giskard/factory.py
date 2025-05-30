from giskard.llm.embeddings import BaseEmbedding
from app.embeddings.giskard.creator import GiskardOllamaEmbeddingsCreator, GiskardOpenAIEmbeddingsCreator
import os
import giskard.llm
from app.config.llm_config import PROVIDER_CONFIGS

class GiskardEmbeddingsFactory():

    _provider_configs = PROVIDER_CONFIGS

    _creators = {
        "ollama/nomic-embed-text:latest": GiskardOllamaEmbeddingsCreator,
        "openai/text-embedding-3-large": GiskardOpenAIEmbeddingsCreator,
    }

    def get_embeddings(self, model: str, **kwargs) -> BaseEmbedding:
        creator_class = self._creators.get(model.lower())
        if not creator_class:
            raise ValueError(f"Unsupported embedding type: {model}")
        creator = creator_class(**kwargs)
        return creator.create_embeddings()

    @classmethod
    def set_global_embedding_model(cls, model_type: str, **kwargs):
        """Set the global embedding model using Giskard's set_embedding_model function."""
        model_provider = model_type.split('/')[0].lower()
        provider_config = cls._provider_configs.get(model_provider, {})
        
        kwargs.update(provider_config)
            
        giskard.llm.set_embedding_model(model_type, **kwargs)

    @classmethod
    def reset_global_embedding_model(cls):
        """Reset the global embedding model to the default model from GSK_EMBEDDING_MODEL environment variable.
        Falls back to "text-embedding-3-small" if the environment variable is not set.
        """
        default_model = os.getenv("GSK_EMBEDDING_MODEL", "text-embedding-3-small")
        cls.set_global_embedding_model(default_model) 