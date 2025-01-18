from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from app.vectorestores.VectorStoreFactory import VectorStoreFactory


class DocArrayInMemorySearchFactory(VectorStoreFactory):

    @staticmethod
    def from_documents(documents, embedding : Embeddings = OpenAIEmbeddings(), collection_name : str = None) -> DocArrayInMemorySearch:
        return DocArrayInMemorySearch.from_documents(
            documents, embedding
        )