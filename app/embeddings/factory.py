from abc import abstractmethod
from langchain_core.embeddings import Embeddings
from giskard.llm.embeddings import BaseEmbedding
from .langchain.factory import LangChainEmbeddingsFactory
from .giskard.factory import GiskardEmbeddingsFactory

class EmbeddingsFactory:
    _factories = {
        "langchain": LangChainEmbeddingsFactory(),
        "giskard": GiskardEmbeddingsFactory()
    }


    @classmethod
    def get_embeddings(cls, model: str, **kwargs) -> Embeddings | BaseEmbedding:
        model_lower = model.lower()
        
        # Split the model string into provider and model name
        try:
            provider, model_name = model_lower.split("/", 1)
        except ValueError:
            raise ValueError(f"Model name must be in format 'provider/model_name'. Got: {model}")
        
        if provider not in cls._factories:
            raise ValueError(f"Unknown provider '{provider}'. Available providers: {', '.join(cls._factories.keys())}")
            
        return cls._factories[provider].get_embeddings(model_name, **kwargs)

    @classmethod
    def available_embeddings(cls):
        all_models = []
        for provider, factory in cls._factories.items():
            models = [f"{provider}/{model}" for model in factory.available_embeddings()]
            all_models.extend(models)
        return all_models
    
    @abstractmethod
    def set_global_embedding_model(cls, model_type: str, **kwargs):
        pass

    @abstractmethod
    def reset_global_embedding_model(cls):
        pass