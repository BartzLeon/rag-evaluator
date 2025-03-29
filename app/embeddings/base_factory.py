from abc import ABC, abstractmethod
from typing import Dict, Type

class BaseEmbeddingsFactory(ABC):
    def __init__(self):
        self._creators: Dict[str, Type] = {}

    @abstractmethod
    def get_embeddings(self, embedding_type: str, **kwargs):
        creator_class = self._creators.get(embedding_type.lower())
        if not creator_class:
            raise ValueError(f"Unsupported embedding type: {embedding_type}")
        creator = creator_class(**kwargs)
        return creator.create_embeddings()

    def available_embeddings(self):
        return list(self._creators.keys()) 