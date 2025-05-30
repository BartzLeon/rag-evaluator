from giskard.llm.client.litellm import LiteLLMClient


from app.chat_models.lite_llm.base import LangChainChatModelCreator
from app.config.llm_config import OPENAI_API_KEY  

class GiskardOpenAILiteLLMCreator(LangChainChatModelCreator):
    def __init__(self, model_name: str):
        self.model_name = model_name

    def create_model(self):
        return LiteLLMClient(
            model=self.model_name,
            completion_params={
                "api_key": OPENAI_API_KEY
            }
        ) 