from langchain_openai import OpenAIEmbeddings
from app.embeddings.langchain.creator.base import LangchainEmbeddingsCreator
from app.config.llm_config import OPENAI_API_KEY
from pydantic import SecretStr

class OpenAIEmbeddingsCreator(LangchainEmbeddingsCreator):
    def __init__(self, dimensions: int = 3072, model: str = "text-embedding-3-large"):
        self.dimensions = dimensions
        self.model = model

    def create_embeddings(self) -> OpenAIEmbeddings:
        return OpenAIEmbeddings(
            dimensions=self.dimensions,
            model=self.model,
            api_key=SecretStr(OPENAI_API_KEY) if OPENAI_API_KEY else None
        )