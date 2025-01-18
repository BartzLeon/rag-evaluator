from langchain_mistralai.chat_models import ChatMistralAI
import os
from langchain_openai.chat_models import ChatOpenAI
from .base import ChatModelCreator
from .config import OPENAI_API_KEY, OPEN_AI_DEFAULT_MODEL

class MistralAIChatModelCreator(ChatModelCreator):
    def __init__(self, model_name: str = OPEN_AI_DEFAULT_MODEL, temperature: float = 0.7):
        self.api_key = OPENAI_API_KEY
        self.model_name = model_name
        self.temperature = temperature

    def create_model(self) -> ChatMistralAI:
        return ChatMistralAI(
            model="mistral-large-latest",
            temperature=0.7,   # Usually between 0.0 - 1.0
            max_retries=2,
            mistral_api_key=os.getenv("MISTRAL_API_KEY"),  # Required in most cases
        )