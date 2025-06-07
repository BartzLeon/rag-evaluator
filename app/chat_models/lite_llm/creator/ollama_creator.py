import os
from giskard.llm.client.litellm import LiteLLMClient

from app.chat_models.lite_llm.base import LangChainChatModelCreator

class GiskardOllamaLiteLLMCreator(LangChainChatModelCreator):
    def __init__(self, model_name: str):
        self.model_name = model_name

    def create_model(self):
        return LiteLLMClient(
            model=self.model_name,
            completion_params={
                "base_url": f"http://{os.getenv('OLLAMA_IP', '192.168.5.2')}:11434",
            }
        )