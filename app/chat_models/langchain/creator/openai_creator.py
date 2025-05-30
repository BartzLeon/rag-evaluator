from langchain_openai.chat_models import ChatOpenAI
from app.chat_models.langchain.base import LangChainChatModelCreator
from pydantic import SecretStr

from app.config.llm_config import OPEN_AI_DEFAULT_MODEL, OPENAI_API_KEY

class OpenAILangChainChatModelCreator(LangChainChatModelCreator):
    model_name_map = {
        "openai/gpt-4": "gpt-4",
        "openai/gpt-4-turbo": "gpt-4-turbo",
        "openai/gpt-4-o": "gpt-4-o",
        "openai/gpt4-o-mini": "gpt-4-o-mini"
    }

    def __init__(self, model_name: str = OPEN_AI_DEFAULT_MODEL, ):
        self.api_key = SecretStr(OPENAI_API_KEY) if OPENAI_API_KEY else None
        self.model_name = self.model_name_map.get(model_name, OPEN_AI_DEFAULT_MODEL)

    def create_model(self) -> ChatOpenAI:
        return ChatOpenAI(
            api_key=self.api_key,
            model=self.model_name,
        )