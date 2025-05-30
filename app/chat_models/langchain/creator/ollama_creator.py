from langchain_ollama import ChatOllama

from app.chat_models.langchain.base import LangChainChatModelCreator

class OllamaLangChainChatModelCreator(LangChainChatModelCreator):
    def __init__(self, model_name: str):
        self.model_name = model_name

    def create_model(self) -> ChatOllama:
        return ChatOllama(
            model=self.model_name,
            base_url="http://192.168.5.2:11434"
        )