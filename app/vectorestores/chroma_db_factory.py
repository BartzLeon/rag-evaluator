from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from chromadb.config import Settings
from app.vectorestores.vector_store_factory import VectorStoreFactory
from app.config.llm_config import OPENAI_API_KEY
from pydantic import SecretStr

class ChromaDBFactory(VectorStoreFactory):

    @staticmethod
    def from_documents(documents = None, embedding : Embeddings = OpenAIEmbeddings(dimensions=3072, model="text-embedding-3-large", api_key=SecretStr(OPENAI_API_KEY) if OPENAI_API_KEY else None), collection_name = "default") -> Chroma:
        vektortore = Chroma(
            collection_name=collection_name,
            embedding_function=embedding,
            persist_directory="app/data/chroma_storage",
            client_settings=Settings(anonymized_telemetry=False)
        )

        if documents is not None:
            vektortore.add_documents(documents)

        return vektortore