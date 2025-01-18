from langchain_openai.chat_models import ChatOpenAI
from .base import ChatModelCreator
from .config import OPENAI_API_KEY, OPEN_AI_DEFAULT_MODEL

class OpenAIChatModelCreator(ChatModelCreator):
    def __init__(self, model_name: str = OPEN_AI_DEFAULT_MODEL, temperature: float = 0.7):
        self.api_key = OPENAI_API_KEY
        self.model_name = model_name
        self.temperature = temperature

    def create_model(self) -> ChatOpenAI:
        return ChatOpenAI(
            api_key=self.api_key,
            model=self.model_name,
            temperature=self.temperature
        )