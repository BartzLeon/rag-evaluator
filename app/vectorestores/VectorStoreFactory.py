from abc import ABC, abstractmethod

from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore


class VectorStoreFactory(ABC):

    @staticmethod
    def from_documents(documents : any, embedding : Embeddings = None, collection_name : str = None) -> VectorStore:
        """Create and return a configured Vector Store."""
        pass