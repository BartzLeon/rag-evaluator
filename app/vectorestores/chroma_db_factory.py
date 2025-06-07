from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from chromadb.config import Settings
from app.vectorestores.vector_store_factory import VectorStoreFactory
from app.config.llm_config import OPENAI_API_KEY
from pydantic import SecretStr

class ChromaDBFactory(VectorStoreFactory):

    @staticmethod
    def from_documents(documents = None, embedding : Embeddings = OpenAIEmbeddings(dimensions=3072, model="text-embedding-3-large", api_key=SecretStr(OPENAI_API_KEY) if OPENAI_API_KEY else None), collection_name = "default", batch_size: int = 5000) -> Chroma:
        vektortore = Chroma(
            collection_name=collection_name,
            embedding_function=embedding,
            persist_directory="app/data/chroma_storage",
            client_settings=Settings(anonymized_telemetry=False)
        )

        if documents is not None:
            # Process documents in batches to avoid ChromaDB batch size limits
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                vektortore.add_documents(batch)
                print(f"Added batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}: {len(batch)} documents")

        return vektortore