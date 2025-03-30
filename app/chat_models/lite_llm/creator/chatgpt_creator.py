from giskard.llm.client.litellm import LiteLLMClient


from app.chat_models.lite_llm.base import LangChainChatModelCreator
from config.llm_config import OPENAI_API_KEY

class GiskardOllamaLiteLLMCreator(LangChainChatModelCreator):
    def __init__(self, model_name: str, temperature: float = 0.7):
        self.model_name = model_name
        self.temperature = temperature

    def create_model(self):
        return LiteLLMClient(
            model=self.model_name,
            completion_params={
                "api_key": OPENAI_API_KEY
            }
        ) 