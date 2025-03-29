from giskard.llm.client.litellm import LiteLLMClient

from app.chat_models.lite_llm.base import LangChainChatModelCreator

class GiskardOllamaLiteLLMCreator(LangChainChatModelCreator):
    def __init__(self, model_name: str, temperature: float = 0.7):
        self.model_name = model_name
        self.temperature = temperature

    def create_model(self):
        return LiteLLMClient(
            model=self.model_name,
            completion_params={
                "base_url": "http://host.docker.internal:11434"
            }
        ) 