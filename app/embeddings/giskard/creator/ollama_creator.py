import os
from .base import GiskardEmbeddingsCreator
from giskard.llm.embeddings.litellm import LiteLLMEmbedding

class GiskardOllamaEmbeddingsCreator(GiskardEmbeddingsCreator):
    def __init__(self, model: str = "ollama/nomic-embed-text:latest", base_url: str = f"http://{os.getenv('OLLAMA_IP', '192.168.5.2')}:11434"):
        self.model = model
        self.base_url = base_url

    def create_embeddings(self) -> LiteLLMEmbedding:
        return LiteLLMEmbedding(
            model=self.model,
            embedding_params={"api_base": self.base_url}
        )