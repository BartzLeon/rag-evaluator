from langchain_openai import OpenAIEmbeddings
from app.embeddings.langchain.creator.base import LangchainEmbeddingsCreator

class OpenAIEmbeddingsCreator(LangchainEmbeddingsCreator):
    def __init__(self, dimensions: int = 3072, model: str = "text-embedding-3-large"):
        self.dimensions = dimensions
        self.model = model

    def create_embeddings(self) -> OpenAIEmbeddings:
        return OpenAIEmbeddings(
            dimensions=self.dimensions,
            model=self.model
        )