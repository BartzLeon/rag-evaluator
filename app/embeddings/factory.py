from langchain_core.embeddings import Embeddings
from giskard.llm.embeddings import BaseEmbedding
from .langchain.factory import LangChainEmbeddingsFactory
from .giskard.factory import GiskardEmbeddingsFactory

class EmbeddingsFactory:
    _langchain_factory = LangChainEmbeddingsFactory()
    _giskard_factory = GiskardEmbeddingsFactory()

    @classmethod
    def get_embeddings(cls, model: str, **kwargs) -> Embeddings | BaseEmbedding:
        model_lower = model.lower()
        
        if model_lower.startswith("langchain/"):
            return cls._langchain_factory.get_embeddings(model_lower[10:], **kwargs)
        elif model_lower.startswith("giskard/"):
            return cls._giskard_factory.get_embeddings(model_lower[8:], **kwargs)
        else:
            raise ValueError(f"Model name must start with either 'langchain/' or 'giskard/'. Got: {model}")

    @classmethod
    def available_embeddings(cls):
        langchain_models = [f"langchain/{model}" for model in cls._langchain_factory.available_embeddings()]
        giskard_models = [f"giskard/{model}" for model in cls._giskard_factory.available_embeddings()]
        return langchain_models + giskard_models