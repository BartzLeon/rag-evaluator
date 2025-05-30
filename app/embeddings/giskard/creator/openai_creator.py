from .base import GiskardEmbeddingsCreator
from giskard.llm.embeddings.litellm import LiteLLMEmbedding
from app.config.llm_config import OPENAI_API_KEY

class GiskardOpenAIEmbeddingsCreator(GiskardEmbeddingsCreator):
    def __init__(self, model: str = "text-embedding-3-large"):
        self.model = model
        self.api_key = OPENAI_API_KEY

    def create_embeddings(self) -> LiteLLMEmbedding:
        return LiteLLMEmbedding(
            model=self.model,
            embedding_params={"api_key": self.api_key}
        )