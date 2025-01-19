from chromadb import Settings
from langchain_chroma import Chroma
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from app.chat_models import config
from app.vectorestores.vector_store_factory import VectorStoreFactory

class ChromaDBFactory(VectorStoreFactory):

    @staticmethod
    def from_documents(documents = None, embedding : Embeddings = OpenAIEmbeddings(dimensions=3072, model="text-embedding-3-large", openai_api_key=config.OPENAI_API_KEY), collection_name = "default") -> Chroma:
        vektortore = Chroma(
            collection_name=collection_name,
            embedding_function=embedding,
            persist_directory="app/data/chroma_storage"  # This is where the data will be saved
        )

        if documents is not None:
            vektortore.add_documents(documents)

        return vektortore